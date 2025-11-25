from typing import Any, Dict

class BotContext:
    """Shared context passed between actions"""
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.cookies: Dict[str, str] = {}
        self.headers: Dict[str, str] = {}
        self.session_active = False
    
    def set(self, key: str, value: Any):
        """Store data in context"""
        self.data[key] = value
    
    def get(self, key: str, default=None) -> Any:
        """Retrieve data from context"""
        return self.data.get(key, default)
    
    def update(self, data: Dict[str, Any]):
        """Update context with multiple values"""
        self.data.update(data)



