import time

from .parsed_message import ParsedMessage

class DeviceRegistry:
    """Track discovered devices with automatic expiry"""
    
    def __init__(self):
        self.devices = {}  # uuid -> DeviceInfo
        
    def register(self, message: ParsedMessage, addr):
        """Register/update a device from NOTIFY or M-SEARCH response"""
        uuid = message.get_uuid()
        cache = message.get_cache_control() or 1800
        
        self.devices[uuid] = {
            'location': message.get_location(),
            'role': message.get_role(),
            'expires_at': time.time() + cache,
            'addr': addr
        }
    
    def remove_expired(self):
        """Remove devices past their cache expiry"""
        now = time.time()
        self.devices = {k: v for k, v in self.devices.items() if v['expires_at'] > now}
    
    def get_devices_by_role(self, role: str):
        """Get all devices matching a role"""
        return [d for d in self.devices.values() if role in d.get('role', '')]