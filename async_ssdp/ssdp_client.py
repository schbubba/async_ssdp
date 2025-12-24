import asyncio
import uuid

from .ssdp_service import SSDPService
from .device_registry import DeviceRegistry
from .parsed_message import ParsedMessage, ParsedMessageType

class SSDPClient:
    """Client that discovers and tracks devices"""
    
    def __init__(self, **kwargs):
        # Client doesn't need device/uuid/location for discovery-only
        self.service = SSDPService(
            device="client", 
            uuid=str(uuid.uuid4()), 
            location="", 
            **kwargs
        )
        self.registry = DeviceRegistry()
    
    async def discover(self, target: str = "ssdp:all", timeout: int = 5):
        """Actively search for devices"""
        await self.service.start_listening()
        
        # Subscribe to responses
        self.service.subscribe(self._on_discovery, [ParsedMessageType.RESPONSE, ParsedMessageType.NOTIFY])
        
        # Send search
        await self.service.broadcast_msearch(target, mx=timeout)
        
        # Wait for responses
        await asyncio.sleep(timeout + 1)
        
        return self.registry.get_all_devices()
    
    async def _on_discovery(self, message: ParsedMessage, addr):
        if message.get_location():
            self.registry.register(message, addr)