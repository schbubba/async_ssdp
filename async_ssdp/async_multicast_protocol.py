import asyncio
import socket
import struct
import platform
from typing import Callable, Tuple



class AsyncMulticastProtocol(asyncio.DatagramProtocol):
    """Simple protocol that just forwards datagrams to a callback"""
    
    def __init__(self, on_datagram: Callable[[bytes, Tuple[str, int]], None]):
        self.on_datagram = on_datagram
        self.transport = None
    
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        """Forward datagram to callback"""
        self.on_datagram(data, addr)
    
    def error_received(self, exc):
        print(f"Protocol error: {exc}")
    
    def connection_lost(self, exc):
        if exc:
            print(f"Connection lost: {exc}")


class MulticastTransport:
    """Handles multicast socket operations"""
    
    def __init__(self, multicast_group: str, multicast_port: int):
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.listener_transport = None
    
    async def send(self, message: str):
        """Send a multicast message"""
        loop = asyncio.get_event_loop()
        
        def _send():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            ttl = struct.pack("b", 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            sock.sendto(message.encode("utf-8"), (self.multicast_group, self.multicast_port))
            sock.close()
        
        await loop.run_in_executor(None, _send)
    
    async def start_listener(self, on_datagram: Callable[[bytes, Tuple[str, int]], None]):
        """Start listening for multicast messages"""
        if self.listener_transport:
            return
        
        loop = asyncio.get_event_loop()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        if platform.system() in ['Darwin', 'FreeBSD', 'OpenBSD', 'NetBSD']:
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except AttributeError:
                pass
        
        sock.bind(("", self.multicast_port))
        
        mreq = struct.pack("4sl", 
                          socket.inet_aton(self.multicast_group),
                          socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        self.listener_transport, _ = await loop.create_datagram_endpoint(
            lambda: AsyncMulticastProtocol(on_datagram),
            sock=sock
        )
    
    def stop_listener(self):
        """Stop listening for multicast messages"""
        if self.listener_transport:
            self.listener_transport.close()
            self.listener_transport = None