from enum import Enum
from typing import Dict, Optional

class ParsedMessageType(Enum):
    NOTIFY = "NOTIFY"
    MSEARCH = "M-SEARCH"
    RESPONSE = "HTTP/1.1"
    UNKNOWN = "UNKNOWN"


class ParsedMessage:
    """Represents a parsed multicast message"""
    
    def __init__(self, message_type: ParsedMessageType, headers: Dict[str, str], status_code: Optional[int] = None):
        self.message_type = message_type
        self.headers = headers
        self.status_code = status_code
    
    def get_header(self, key: str, default=None):
        """Case-insensitive header lookup"""
        key_lower = key.lower()
        for k, v in self.headers.items():
            if k.lower() == key_lower:
                return v
        return default
    
    def is_notification(self) -> bool:
        return self.message_type == ParsedMessageType.NOTIFY
    
    def is_search(self) -> bool:
        return self.message_type == ParsedMessageType.MSEARCH
    
    def is_response(self) -> bool:
        return self.message_type == ParsedMessageType.RESPONSE
    
    def get_notification_type(self) -> Optional[str]:
        return self.get_header('NTS')
    
    def get_role(self) -> Optional[str]:
        role = self.get_header('NT')
        if not role and self.message_type == ParsedMessageType.MSEARCH:
            role = self.get_header('SOURCE')
        if not role and self.message_type == ParsedMessageType.RESPONSE:
            role = self.get_search_target()
        return role
    
    def get_search_target(self) -> Optional[str]:
        return self.get_header('ST')
    
    def get_location(self) -> Optional[str]:
        return self.get_header('LOCATION')
    
    def get_usn(self) -> Optional[str]:
        return self.get_header('USN')
    
    def get_uuid(self) -> Optional[str]:
        usn = self.get_usn()
        if usn and usn.startswith('uuid:'):
            parts = usn[5:].split('::')
            return parts[0] if parts else None
        return None
    
    def get_max_wait(self) -> Optional[int]:
        mx = self.get_header('MX')
        return int(mx) if mx else None
    
    def get_cache_control(self) -> Optional[int]:
        cc = self.get_header('CACHE-CONTROL')
        if cc and 'max-age=' in cc:
            try:
                return int(cc.split('max-age=')[1].split(',')[0].strip())
            except (ValueError, IndexError):
                return None
        return None