"""Core Bot System.

Main bot orchestrator that manages all modules and interactions.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from .config import ConfigManager
from .infrastructure.event_bus import EventBus, Event
from .ethics.core import EthicsCore
from .consciousness.core import ConsciousnessCore
from .memory.core import MemoryCore

logger = logging.getLogger('core_bot')

class InfinityBot:
    """Main bot orchestrator."""
    
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.event_bus: Optional[EventBus] = None
        self.ethics: Optional[EthicsCore] = None
        self.consciousness: Optional[ConsciousnessCore] = None
        self.memory: Optional[MemoryCore] = None
        self.is_running: bool = False
        self._tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self, config_path: str = None) -> None:
        """Initialize the bot and all its components."""
        try:
            # Initialize config
            self.config_manager = ConfigManager(config_path)
            await self.config_manager.initialize()
            
            # Initialize event bus
            self.event_bus = EventBus(
                history_size=self.config_manager.config.event_history_size
            )
            
            # Initialize core modules
            await self._initialize_core_modules()
            
            # Subscribe to system events
            self._setup_event_handlers()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            raise
            
    async def _initialize_core_modules(self) -> None:
        """Initialize core system modules."""
        try:
            if self.config_manager.is_module_enabled("ethics"):
                self.ethics = await EthicsCore.initialize(self.event_bus)
                
            if self.config_manager.is_module_enabled("consciousness"):
                self.consciousness = await ConsciousnessCore.initialize(self.event_bus)
                
            if self.config_manager.is_module_enabled("memory"):
                self.memory = await MemoryCore.initialize(self.event_bus)
                
        except Exception as e:
            logger.error(f"Error initializing core modules: {str(e)}")
            raise
            
    def _setup_event_handlers(self) -> None:
        """Setup handlers for system events."""
        self.event_bus.subscribe("system.shutdown", self._handle_shutdown)
        self.event_bus.subscribe("system.reload_config", self._handle_reload_config)
        self.event_bus.subscribe("system.status_request", self._handle_status_request)
        
    async def start(self) -> None:
        """Start the bot and all its components."""
        if self.is_running:
            logger.warning("Bot is already running")
            return
            
        try:
            self.is_running = True
            
            # Start maintenance task
            self._tasks["maintenance"] = asyncio.create_task(
                self._run_maintenance()
            )
            
            # Publish startup event
            await self.event_bus.publish(Event(
                type="system.startup",
                data={"timestamp": datetime.now().isoformat()},
                source="core_bot"
            ))
            
            logger.info("Bot started successfully")
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start bot: {str(e)}")
            raise
            
    async def stop(self) -> None:
        """Stop the bot and all its components."""
        if not self.is_running:
            return
            
        try:
            self.is_running = False
            
            # Cancel all running tasks
            for task in self._tasks.values():
                if not task.done():
                    task.cancel()
                    
            # Wait for tasks to complete
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
            
            # Publish shutdown event
            await self.event_bus.publish(Event(
                type="system.shutdown",
                data={"timestamp": datetime.now().isoformat()},
                source="core_bot"
            ))
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            raise
            
    async def _run_maintenance(self) -> None:
        """Run periodic maintenance tasks."""
        while self.is_running:
            try:
                # Check config updates
                await self.config_manager.reload_if_needed()
                
                # Run module-specific maintenance
                if self.memory:
                    await self.memory._run_maintenance()
                    
                # Sleep for maintenance interval
                await asyncio.sleep(60)  # 1 minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in maintenance task: {str(e)}")
                await asyncio.sleep(5)
                
    async def _handle_shutdown(self, event: Event) -> None:
        """Handle system shutdown event."""
        await self.stop()
        
    async def _handle_reload_config(self, event: Event) -> None:
        """Handle config reload request."""
        try:
            await self.config_manager.load_config()
            logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {str(e)}")
            
    async def _handle_status_request(self, event: Event) -> None:
        """Handle system status request."""
        try:
            status = {
                "is_running": self.is_running,
                "start_time": self._tasks.get("maintenance", {}).get("start_time"),
                "enabled_modules": [
                    m for m, enabled 
                    in self.config_manager.config.enabled_modules.items()
                    if enabled
                ],
                "performance_metrics": (
                    self.config_manager.get_performance_metrics()
                ),
                "event_bus_stats": {
                    "subscribers": len(self.event_bus._subscribers),
                    "history_size": len(self.event_bus._history)
                }
            }
            
            await self.event_bus.publish(Event(
                type="system.status_response",
                data=status,
                source="core_bot"
            ))
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            
    async def process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming message through the system."""
        try:
            # Create message event
            event = Event(
                type="message.received",
                data=message,
                source="core_bot"
            )
            
            # Validate with ethics if enabled
            if self.ethics:
                validation = await self.ethics.validate_action({
                    "action_type": "process_message",
                    "content": message.get("content", ""),
                    "metadata": message
                })
                
                if not validation.get("is_valid", False):
                    await self.event_bus.publish(Event(
                        type="message.rejected",
                        data={
                            "reason": validation.get("reason", "Ethics validation failed"),
                            "original_message": message
                        },
                        source="core_bot"
                    ))
                    return
                    
            # Store in memory if enabled
            if self.memory:
                await self.memory.store_memory({
                    "content": message,
                    "context": {"type": "message"},
                    "memory_type": "interaction",
                    "importance": 0.5
                })
                
            # Update consciousness if enabled
            if self.consciousness:
                await self.consciousness.process_interaction(message)
                
            # Publish processed message event
            await self.event_bus.publish(Event(
                type="message.processed",
                data=message,
                source="core_bot"
            ))
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.event_bus.publish(Event(
                type="message.error",
                data={
                    "error": str(e),
                    "original_message": message
                },
                source="core_bot"
            ))
            
    async def get_response(self, message_id: str) -> Optional[Dict]:
        """Get system response for a message."""
        try:
            if self.memory:
                # Retrieve context from memory
                memory = await self.memory.get_memory(message_id)
                if not memory:
                    return None
                    
                return {
                    "response": "Response based on memory and context",
                    "context": memory.context
                }
                
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return None 