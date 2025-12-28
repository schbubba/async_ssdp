import asyncio
from .message_builder import MessageBuilder
from .async_multicast_protocol import MulticastTransport
from .event_bus import EventBus
from .message_parser import MessageParser, MessageSubType
from .parsed_message import ParsedMessageType

from typing import List, Callable, Tuple

class SSDPService:
    """High-level SSDP service orchestrator"""
    
    def __init__(self, 
                 device: str,
                 uuid: str,
                 location: str,
                 cache: int = 1800,
                 json_upnp: bool = False,
                 multicast_group: str = '224.0.0.251',
                #  multicast_group: str = '239.255.255.250',
                 multicast_port: int = 1900):
        
        schema = "urn:schemas-json-upnp-org" if json_upnp else "urn:schemas-upnp-org"
        
        self.message_builder = MessageBuilder(
            device, uuid, location, schema, 
            multicast_group, multicast_port, cache
        )
        self.transport = MulticastTransport(multicast_group, multicast_port)
        self.event_bus = EventBus()
        self.parser = MessageParser()
        self._is_listening = False
    
    async def broadcast_alive(self, status: MessageSubType=None):
        """Broadcast an 'alive' notification"""
        message = self.message_builder.build_notify('alive', status)
        await self.transport.send(message)
    
    async def broadcast_byebye(self):
        """Broadcast a 'byebye' notification"""
        message = self.message_builder.build_notify('byebye')
        await self.transport.send(message)
    
    async def broadcast_msearch(self, target: str, mx: int = 5):
        """Broadcast an M-SEARCH request"""
        message = self.message_builder.build_msearch_request(target, mx)
        await self.transport.send(message)
    
    async def broadcast_msearch_response(self, target: str):
        """Broadcast an M-SEARCH response"""
        message = self.message_builder.build_msearch_response(target)
        await self.transport.send(message)
    
    async def start_listening(self):
        """Start listening for multicast messages"""
        if self._is_listening:
            return
        
        await self.transport.start_listener(self._on_datagram)
        self._is_listening = True
    
    async def stop_listening(self):
        """Stop listening for multicast messages"""
        self.transport.stop_listener()
        self._is_listening = False
    
    def _on_datagram(self, data: bytes, addr: Tuple[str, int]):
        """Handle received datagram"""
        message = self.parser.parse(data)
        if message:
            # Schedule async publish
            asyncio.create_task(self.event_bus.publish(message, addr))
    
    def subscribe(self, callback: Callable, message_types: List[ParsedMessageType] = None):
        """Subscribe to SSDP messages"""
        self.event_bus.subscribe(callback, message_types)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from SSDP messages"""
        self.event_bus.unsubscribe(callback)