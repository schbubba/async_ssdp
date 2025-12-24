import asyncio
from typing import Callable, List, Tuple

from .parsed_message import ParsedMessage, ParsedMessageType

class EventBus:
    """Simple event bus for message distribution"""
    
    def __init__(self):
        self.subscribers: List[Tuple[Callable, List[ParsedMessageType]]] = []
    
    def subscribe(self, callback: Callable, message_types: List[ParsedMessageType] = None):
        """Subscribe to messages with optional type filtering"""
        filters = message_types or []
        self.subscribers.append((callback, filters))
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from messages"""
        self.subscribers = [(cb, filters) for cb, filters in self.subscribers if cb != callback]
    
    async def publish(self, message: ParsedMessage, addr: Tuple[str, int]):
        """Publish a message to all interested subscribers"""
        for callback, filters in self.subscribers:
            # If no filters, accept all messages
            if not filters or message.message_type in filters:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message, addr)
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        None, callback, message, addr
                    )