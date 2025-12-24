
from .ssdp_service import SSDPService
from .periodic_announcer import PeriodicAnnouncer
from .ssdp_responder import SSDPResponder
from .parsed_message import ParsedMessageType

class SSDPServer:
    """Server that announces itself and responds to searches"""
    
    def __init__(self, device: str, uuid: str, location: str, **kwargs):
        self.service = SSDPService(device, uuid, location, **kwargs)
        self.announcer = PeriodicAnnouncer(self.service)
        self.responder = SSDPResponder(self.service, ["ssdp:all", f"urn:schemas-upnp-org:device:{device}:1"])
    
    async def start(self):
        await self.service.start_listening()
        self.service.subscribe(self.responder.handle_search, [ParsedMessageType.MSEARCH])
        await self.announcer.start()
    
    async def stop(self):
        await self.announcer.stop()
        await self.service.stop_listening()