
from .ssdp_service import SSDPService

class PeriodicAnnouncer:
    """Sends periodic alive messages"""
    
    def __init__(self, service: SSDPService, interval: int = 600):
        self.service = service
        self.interval = interval
        self.task = None
    
    async def start(self):
        """Start periodic announcements"""
        self.task = asyncio.create_task(self._announce_loop())
    
    async def stop(self):
        """Stop announcements and send byebye"""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        await self.service.broadcast_byebye()
    
    async def _announce_loop(self):
        """Announce alive periodically"""
        while True:
            await self.service.broadcast_alive()
            await asyncio.sleep(self.interval)