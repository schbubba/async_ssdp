import asyncio
import random
from typing import List
from .ssdp_service import SSDPService
from .parsed_message import ParsedMessage

class SSDPResponder:
    """Automatically responds to M-SEARCH requests"""
    
    def __init__(self, service: SSDPService, match_targets: List[str]):
        self.service = service
        self.match_targets = match_targets  # e.g., ["ssdp:all", "upnp:rootdevice", "urn:schemas-upnp-org:device:miner:1"]
        
    async def handle_search(self, message: ParsedMessage, addr):
        if message.is_search():
            target = message.get_search_target()
            if target in self.match_targets or "ssdp:all" in [target]:
                # Respect MX (random delay)
                mx = message.get_max_wait() or 3
                delay = random.uniform(0, mx)
                await asyncio.sleep(delay)
                await self.service.broadcast_msearch_response(target)