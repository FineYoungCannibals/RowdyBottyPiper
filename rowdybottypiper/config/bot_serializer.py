"""
Bot Serializer for RowdyBottyPiper
Handles serialization/deserialization of actions between different formats
"""

import json
from typing import List, Dict, Any
from pydantic import TypeAdapter

from rowdybottypiper.actions.action import Action
from rowdybottypiper.config.action_registry import ActionUnion


class BotSerializer:
    """Serialize and deserialize bot actions between formats"""
    
    # Create a TypeAdapter for the ActionUnion
    # This handles the discriminated union parsing
    _action_adapter = TypeAdapter(ActionUnion)
    
    @staticmethod
    def actions_to_json(actions: List[Action], indent: int = 2) -> str:
        """
        Serialize a list of actions to a JSON string
        
        Args:
            actions: List of Action instances
            indent: JSON indentation (default 2 for readability)
            
        Returns:
            JSON string representation of actions
        """
        action_dicts = [action.model_dump(mode='json') for action in actions]
        return json.dumps(action_dicts, indent=indent)
    
    @staticmethod
    def json_to_actions(json_str: str) -> List[Action]:
        """
        Deserialize a JSON string to a list of actions
        Uses discriminated union to automatically determine action types
        
        Args:
            json_str: JSON string containing action configurations
            
        Returns:
            List of Action instances
            
        Raises:
            ValueError: If JSON is invalid or action types are unknown
        """
        try:
            data = json.loads(json_str)
            
            # Handle both single action and list of actions
            if isinstance(data, dict):
                data = [data]
            
            if not isinstance(data, list):
                raise ValueError("JSON must be a list of action objects or a single action object")
            
            # Use TypeAdapter to parse each action with discriminated union
            actions = [BotSerializer._action_adapter.validate_python(action_data) for action_data in data]
            return actions
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse actions: {e}")
    
    @staticmethod
    def actions_to_dict(actions: List[Action]) -> List[Dict[str, Any]]:
        """
        Convert actions to a list of dictionaries
        Useful for YAML export or other dict-based formats
        
        Args:
            actions: List of Action instances
            
        Returns:
            List of dictionaries representing actions
        """
        return [action.model_dump(mode='python') for action in actions]
    
    @staticmethod
    def dict_to_actions(action_dicts: List[Dict[str, Any]]) -> List[Action]:
        """
        Convert a list of dictionaries to actions
        Useful for loading from YAML or other dict-based formats
        
        Args:
            action_dicts: List of dictionaries with action configurations
            
        Returns:
            List of Action instances
            
        Raises:
            ValueError: If action configurations are invalid
        """
        if not isinstance(action_dicts, list):
            raise ValueError("action_dicts must be a list")
        
        try:
            # Use TypeAdapter to parse each action with discriminated union
            actions = [BotSerializer._action_adapter.validate_python(action_data) for action_data in action_dicts]
            return actions
        except Exception as e:
            raise ValueError(f"Failed to parse actions from dicts: {e}")
    
    @staticmethod
    def action_to_json(action: Action, indent: int = 2) -> str:
        """
        Serialize a single action to JSON string
        
        Args:
            action: Action instance
            indent: JSON indentation
            
        Returns:
            JSON string representation of the action
        """
        return json.dumps(action.model_dump(mode='json'), indent=indent)
    
    @staticmethod
    def json_to_action(json_str: str) -> Action:
        """
        Deserialize a JSON string to a single action
        
        Args:
            json_str: JSON string containing action configuration
            
        Returns:
            Action instance
            
        Raises:
            ValueError: If JSON is invalid or action type is unknown
        """
        try:
            data = json.loads(json_str)
            return BotSerializer._action_adapter.validate_python(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse action: {e}")