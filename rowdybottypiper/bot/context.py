from typing import Any, Dict

class Context:
    """Bots use this object to save data regarding their session"""
    data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any):
        """Store data in context"""
        self.data[key] = value
    
    def get(self, key: str, default=None) -> Any:
        """Retrieve data from context"""
        return self.data.get(key, default)
    
    def update(self, data: Dict[str, Any]):
        """Update context with multiple values"""
        self.data.update(data)