from typing import Optional, Literal

from .parsed_message import ParsedMessage, ParsedMessageType

class MessageParser:
    """Parses raw bytes into ParsedMessage objects"""
    
    @staticmethod
    def parse(data: bytes) -> Optional[ParsedMessage]:
        try:
            text = data.decode('utf-8').strip()
            if not text:
                return None
            
            lines = text.split('\r\n')
            if not lines:
                return None
            
            first_line = lines[0].strip()
            message_type = ParsedMessageType.UNKNOWN
            status_code = None
            
            if first_line.startswith('NOTIFY'):
                message_type = ParsedMessageType.NOTIFY
            elif first_line.startswith('M-SEARCH'):
                message_type = ParsedMessageType.MSEARCH
            elif first_line.startswith('HTTP/1.1'):
                message_type = ParsedMessageType.RESPONSE
                parts = first_line.split()
                if len(parts) >= 2:
                    try:
                        status_code = int(parts[1])
                    except ValueError:
                        pass
            
            headers = {}
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            return ParsedMessage(text, message_type, headers, status_code)
            
        except UnicodeDecodeError:
            print("Failed to decode message as UTF-8")
            return None
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None


MessageType = Literal["alive", "byebye"]
MessageSubType = Literal["stopped", "running", "paused", "stopping"]