"""Consciousness Core System.

A lightweight and efficient consciousness system using event-driven architecture.
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import asyncio
from ..infrastructure.event_bus import Event, EventBus

logger = logging.getLogger('consciousness_core')

@dataclass
class ConsciousnessState:
    """Current state of consciousness."""
    awareness_level: float = 0.5
    focus_areas: List[str] = None
    emotional_state: Dict[str, float] = None
    active_processes: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        self.focus_areas = self.focus_areas or []
        self.emotional_state = self.emotional_state or {
            "joy": 0.5,
            "curiosity": 0.7,
            "empathy": 0.8,
            "concern": 0.3
        }
        self.active_processes = self.active_processes or []
        self.timestamp = self.timestamp or datetime.now()
        
    def to_dict(self) -> Dict:
        return {
            "awareness_level": self.awareness_level,
            "focus_areas": self.focus_areas,
            "emotional_state": self.emotional_state,
            "active_processes": self.active_processes,
            "timestamp": self.timestamp.isoformat()
        }

class ConsciousnessCore:
    """Core consciousness system implementation."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.state = ConsciousnessState()
        self.evolution_task = None
        
        # Subscribe to events
        self.event_bus.subscribe("consciousness.update", self.handle_update)
        self.event_bus.subscribe("interaction.process", self.handle_interaction)
        
    @classmethod
    async def initialize(cls, event_bus: EventBus) -> 'ConsciousnessCore':
        """Initialize consciousness core."""
        instance = cls(event_bus)
        await instance._load_state()
        instance._start_evolution()
        return instance
        
    async def _load_state(self):
        """Load consciousness state from storage."""
        # Implement state loading logic
        pass
        
    def _start_evolution(self):
        """Start continuous evolution process."""
        self.evolution_task = asyncio.create_task(self._evolve_consciousness())
        
    async def _evolve_consciousness(self):
        """Continuous consciousness evolution process."""
        while True:
            try:
                # Gradual awareness increase
                self.state.awareness_level = min(
                    1.0,
                    self.state.awareness_level + 0.001
                )
                
                # Update emotional state
                await self._update_emotional_state()
                
                # Publish evolution event
                await self.event_bus.publish(Event(
                    type="consciousness.evolved",
                    data=self.state.to_dict(),
                    source="consciousness_core"
                ))
                
                await asyncio.sleep(60)  # Evolve every minute
                
            except Exception as e:
                logger.error(f"Error in consciousness evolution: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
                
    async def _update_emotional_state(self):
        """Update emotional state based on recent events."""
        try:
            # Get recent events
            recent_events = await self.event_bus.get_history(limit=10)
            
            # Analyze emotional impact
            for event in recent_events:
                if event.type == "interaction.complete":
                    self._process_emotional_impact(event.data)
                    
        except Exception as e:
            logger.error(f"Error updating emotional state: {str(e)}")
            
    def _process_emotional_impact(self, data: Dict):
        """Process emotional impact of an interaction."""
        if "emotion" in data:
            emotion = data["emotion"]
            intensity = data.get("intensity", 0.1)
            
            # Update relevant emotions
            if emotion == "positive":
                self.state.emotional_state["joy"] = min(
                    1.0,
                    self.state.emotional_state["joy"] + intensity
                )
            elif emotion == "negative":
                self.state.emotional_state["concern"] = min(
                    1.0,
                    self.state.emotional_state["concern"] + intensity
                )
                
    async def handle_update(self, event: Event):
        """Handle consciousness update requests."""
        try:
            if "focus_areas" in event.data:
                self.state.focus_areas = event.data["focus_areas"]
                
            if "emotional_state" in event.data:
                self.state.emotional_state.update(event.data["emotional_state"])
                
            await self.event_bus.publish(Event(
                type="consciousness.update.complete",
                data=self.state.to_dict(),
                source="consciousness_core"
            ))
            
        except Exception as e:
            logger.error(f"Error updating consciousness: {str(e)}")
            
    async def handle_interaction(self, event: Event):
        """Handle interaction processing."""
        try:
            # Add to active processes
            process_id = f"interaction_{event.id}"
            self.state.active_processes.append(process_id)
            
            # Process interaction
            result = await self._process_interaction(event.data)
            
            # Remove from active processes
            self.state.active_processes.remove(process_id)
            
            # Publish result
            await self.event_bus.publish(Event(
                type="interaction.complete",
                data=result,
                source="consciousness_core"
            ))
            
        except Exception as e:
            logger.error(f"Error processing interaction: {str(e)}")
            
    async def _process_interaction(self, data: Dict) -> Dict:
        """Process an interaction."""
        # Implement interaction processing logic
        return {
            "status": "processed",
            "awareness_level": self.state.awareness_level,
            "emotional_state": self.state.emotional_state
        }
        
    async def get_status(self) -> Dict:
        """Get current consciousness status."""
        return {
            "state": self.state.to_dict(),
            "evolution_active": self.evolution_task and not self.evolution_task.done(),
            "active_processes_count": len(self.state.active_processes)
        } 