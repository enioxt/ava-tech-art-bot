"""Event Bus for inter-module communication.

This module implements a publish-subscribe pattern for asynchronous
event-driven communication between system modules.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger('event_bus')

@dataclass
class Event:
    """Event data structure."""
    type: str
    data: Dict
    source: str
    timestamp: datetime = None
    id: str = None
    
    def __post_init__(self):
        """Initialize optional fields."""
        from uuid import uuid4
        self.timestamp = self.timestamp or datetime.now()
        self.id = self.id or str(uuid4())
        
    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create event from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

class EventBus:
    """Event bus implementation with async support."""
    
    def __init__(self, history_size: int = 1000):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history = history_size
        self._lock = asyncio.Lock()
        
    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        try:
            async with self._lock:
                # Store in history
                self._history.append(event)
                if len(self._history) > self._max_history:
                    self._history.pop(0)
                    
                # Notify subscribers
                if event.type in self._subscribers:
                    for callback in self._subscribers[event.type]:
                        try:
                            await callback(event)
                        except Exception as e:
                            logger.error(f"Error in event handler: {str(e)}")
                            
                logger.debug(f"Published event: {event.type}")
                
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")
            
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"New subscriber for: {event_type}")
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
                
    async def get_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history, optionally filtered by type."""
        async with self._lock:
            if event_type:
                filtered = [e for e in self._history if e.type == event_type]
                return filtered[-limit:]
            return self._history[-limit:]
            
    async def clear_history(self):
        """Clear event history."""
        async with self._lock:
            self._history.clear()
            
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers.get(event_type, []))
        
    async def replay_events(
        self,
        callback: Callable,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None
    ):
        """Replay historical events to a callback."""
        async with self._lock:
            for event in self._history:
                if event_type and event.type != event_type:
                    continue
                if start_time and event.timestamp < start_time:
                    continue
                await callback(event)