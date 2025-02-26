"""Memory Core System.

A lightweight and efficient memory system using event-driven architecture.
"""

import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from ..infrastructure.event_bus import Event, EventBus

logger = logging.getLogger('memory_core')

@dataclass
class Memory:
    """Memory data structure."""
    content: Any
    context: Dict
    memory_type: str
    importance: float = 0.5
    timestamp: datetime = None
    id: str = None
    
    def __post_init__(self):
        from uuid import uuid4
        self.timestamp = self.timestamp or datetime.now()
        self.id = self.id or str(uuid4())
        
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "context": self.context,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

class MemoryCore:
    """Core memory system implementation."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.memories: Dict[str, Memory] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.maintenance_task = None
        
        # Subscribe to events
        self.event_bus.subscribe("memory.store", self.handle_store)
        self.event_bus.subscribe("memory.retrieve", self.handle_retrieve)
        self.event_bus.subscribe("memory.search", self.handle_search)
        
    @classmethod
    async def initialize(cls, event_bus: EventBus) -> 'MemoryCore':
        """Initialize memory core."""
        instance = cls(event_bus)
        await instance._load_state()
        instance._start_maintenance()
        return instance
        
    async def _load_state(self):
        """Load memory state from storage."""
        # Implement state loading logic
        pass
        
    def _start_maintenance(self):
        """Start maintenance process."""
        self.maintenance_task = asyncio.create_task(self._run_maintenance())
        
    async def _run_maintenance(self):
        """Run periodic maintenance tasks."""
        while True:
            try:
                await self._clean_cache()
                await self._consolidate_memories()
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in memory maintenance: {str(e)}")
                await asyncio.sleep(5)
                
    async def _clean_cache(self):
        """Clean expired cache entries."""
        now = datetime.now().timestamp()
        expired = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp > self.cache_ttl
        ]
        for key in expired:
            del self.cache[key]
            
    async def _consolidate_memories(self):
        """Consolidate and optimize memories."""
        # Implement memory optimization logic
        pass
        
    async def handle_store(self, event: Event):
        """Handle memory storage requests."""
        try:
            memory = Memory(**event.data)
            await self.store_memory(memory)
            
            await self.event_bus.publish(Event(
                type="memory.store.complete",
                data={"memory_id": memory.id},
                source="memory_core"
            ))
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            await self.event_bus.publish(Event(
                type="memory.store.error",
                data={"error": str(e)},
                source="memory_core"
            ))
            
    async def handle_retrieve(self, event: Event):
        """Handle memory retrieval requests."""
        try:
            memory_id = event.data["memory_id"]
            memory = await self.get_memory(memory_id)
            
            if memory:
                await self.event_bus.publish(Event(
                    type="memory.retrieve.complete",
                    data=memory.to_dict(),
                    source="memory_core"
                ))
            else:
                await self.event_bus.publish(Event(
                    type="memory.retrieve.not_found",
                    data={"memory_id": memory_id},
                    source="memory_core"
                ))
                
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            
    async def handle_search(self, event: Event):
        """Handle memory search requests."""
        try:
            results = await self.search_memories(event.data)
            
            await self.event_bus.publish(Event(
                type="memory.search.complete",
                data={"results": [m.to_dict() for m in results]},
                source="memory_core"
            ))
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            
    async def store_memory(self, memory: Memory):
        """Store a new memory."""
        self.memories[memory.id] = memory
        self._update_cache(memory)
        
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        # Check cache first
        cache_key = f"memory_{memory_id}"
        if cache_key in self.cache:
            return self.cache[cache_key][0]
            
        # Get from storage
        memory = self.memories.get(memory_id)
        if memory:
            self._update_cache(memory)
            
        return memory
        
    def _update_cache(self, memory: Memory):
        """Update memory cache."""
        cache_key = f"memory_{memory.id}"
        self.cache[cache_key] = (memory, datetime.now().timestamp())
        
    async def search_memories(
        self,
        criteria: Dict,
        limit: int = 10
    ) -> List[Memory]:
        """Search memories based on criteria."""
        results = []
        
        for memory in self.memories.values():
            if self._matches_criteria(memory, criteria):
                results.append(memory)
                
            if len(results) >= limit:
                break
                
        return results
        
    def _matches_criteria(self, memory: Memory, criteria: Dict) -> bool:
        """Check if memory matches search criteria."""
        for key, value in criteria.items():
            if key == "memory_type" and memory.memory_type != value:
                return False
            if key == "min_importance" and memory.importance < value:
                return False
            if key == "start_time" and memory.timestamp < value:
                return False
            if key == "end_time" and memory.timestamp > value:
                return False
                
        return True
        
    async def get_status(self) -> Dict:
        """Get current memory system status."""
        return {
            "total_memories": len(self.memories),
            "cache_size": len(self.cache),
            "maintenance_active": self.maintenance_task and not self.maintenance_task.done(),
            "last_update": datetime.now().isoformat()
        } 