
import platform
from typing import List
from email.utils import formatdate

from .message_parser import MessageType, MessageSubType

class MessageBuilder:
    """Builds SSDP protocol messages"""
    
    def __init__(self, device: str, uuid: str, location: str, schema: str, 
                 multicast_group: str, multicast_port: int, cache: int = 1800):
        self.device = device
        self.uuid = uuid
        self.location = location
        self.schema = schema
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.cache = cache
        self.json_upnp = "json" in schema
    
    def build_notify(self, type: MessageType, sub_type: MessageSubType = None) -> str:
        """Build a NOTIFY message (alive/byebye)"""
        os_name = platform.system()
        os_release = platform.version()
        server_upnp = "json-UPnP/1.0" if self.json_upnp else "UPnp/1.0"
        
        nts = f"{type}" if not sub_type else f"{type}::{sub_type}"
        
        args = [
            "NOTIFY * HTTP/1.0",
            f"HOST: {self.multicast_group}:{self.multicast_port}",
            f"NT: urn:{self.schema}:{self.device}:1",
            f"NTS: ssdp:{nts}",
            f"LOCATION: {self.location}",
            f"USN: uuid:{self.uuid}::{self.schema}:{self.device}:1",
            f"CACHE-CONTROL: max-age={self.cache}",
            f"SERVER: {os_name}/{os_release} {server_upnp} {self.device}/1.0"
        ]
        
        return self._build_message(args)
    
    def build_msearch_request(self, target: str, mx: int = 5) -> str:
        """Build an M-SEARCH request message"""
        args = [
            "M-SEARCH * HTTP/1.1",
            f"HOST: {self.multicast_group}:{self.multicast_port}",
            f"MAN: \"ssdp:discover\"",
            f"MX: {mx}",
            f"ST: {target}"
        ]
        
        return self._build_message(args)
    
    def build_msearch_response(self, target: str) -> str:
        """Build an M-SEARCH response message"""
        os_name = platform.system()
        os_release = platform.version()
        server_upnp = "json-UPnP/1.0" if self.json_upnp else "UPnp/1.0"
        
        args = [
            "HTTP/1.1 200 OK",
            f"CACHE-CONTROL: max-age={self.cache}",
            f"DATE: {formatdate(usegmt=True)}",
            f"EXT: ",
            f"LOCATION: {self.location}",
            f"SERVER: {os_name}/{os_release} {server_upnp} {self.device}/1.0",
            f"ST: ssdp:{target}",
            f"USN: uuid:{self.uuid}::{self.schema}:device:{self.device}",
        ]
        
        return self._build_message(args)
    
    @staticmethod
    def _build_message(args: List[str]) -> str:
        """Build a message from a list of headers"""
        return "\r\n".join(args) + "\r\n\r\n"