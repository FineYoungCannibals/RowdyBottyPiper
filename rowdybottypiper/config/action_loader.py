"""
YAML Configuration Loader for RowdyBottyPiper
Allows users to define bot workflows in YAML format
"""

import yaml
import os
import re
from typing import Dict, Any, List
from pathlib import Path

from rowdybottypiper.actions.action import Action
from rowdybottypiper.config.action_registry import ACTION_REGISTRY
from rowdybottypiper.config.bot_serializer import BotSerializer


class ActionLoader:
    """Load bot configuration from YAML files"""
    
    def __init__(self, config_path: str):
        """
        Initialize loader with YAML config file path
        
        Args:
            config_path: Path to YAML config file
        """
        self.config_path = Path(config_path)
        self.config = self._load_yaml_file(config_path)
        # Process variables and environment substitution
        self.variables = self.config.get('variables', {})
        self._resolve_variables()
    
    def _load_yaml_file(self, config_path: str) -> Dict[str, Any]:
        """Load YAML file and return as dictionary"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """
        Recursively substitute environment variables in format ${VAR_NAME}
        
        Args:
            value: Value to process (can be str, dict, list, or other)
            
        Returns:
            Value with environment variables substituted
        """
        if isinstance(value, str):
            # Find all ${VAR_NAME} patterns
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            
            for var_name in matches:
                # Check variables dict first, then environment
                replacement = self.variables.get(var_name) or os.getenv(var_name, '')
                value = value.replace(f'${{{var_name}}}', str(replacement))
            
            if '~' in value:
                value = os.path.expanduser(value)
                
            return value
        
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        
        else:
            return value
    
    def _resolve_variables(self):
        """Resolve all variables and environment substitutions in config"""
        # First resolve variables section itself
        self.variables = self._substitute_env_vars(self.variables)
        
        # Then resolve the entire config
        self.config = self._substitute_env_vars(self.config)
    
    def _normalize_action_config(self, action_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize action config from YAML format to Pydantic format
        
        YAML uses 'type' field with friendly names like 'login', 'click'
        Pydantic expects 'type' field with class names like 'LoginAction', 'ClickAction'
        
        Args:
            action_config: Raw action config from YAML
            
        Returns:
            Normalized config ready for Pydantic parsing
        """
        config_copy = action_config.copy()
        action_type = config_copy.get('type')
        
        if not action_type:
            raise ValueError("Action config missing 'type' field")
        
        # Get the action class from registry
        action_class = ACTION_REGISTRY.get(action_type)
        if not action_class:
            raise ValueError(
                f"Unknown action type: '{action_type}'. "
                f"Available types: {', '.join(ACTION_REGISTRY.keys())}"
            )
        
        # Replace friendly type name with Pydantic discriminator value
        # e.g., 'login' -> 'LoginAction'
        config_copy['type'] = action_class.__fields__['type'].default
        
        return config_copy
    
    def load_actions(self) -> List[Action]:
        """
        Load actions from the YAML configuration
        
        Returns:
            List of Action instances
        """
        actions_config = self.config.get('actions', [])
        
        if not actions_config:
            raise ValueError("No actions found in configuration")
        
        # Normalize and convert to actions using BotSerializer
        normalized_configs = [self._normalize_action_config(ac) for ac in actions_config]
        actions = BotSerializer.dict_to_actions(normalized_configs)
        
        return actions
    
    def get_bot_config(self) -> Dict[str, Any]:
        """
        Get bot configuration (non-action settings)
        
        Returns:
            Dictionary with bot configuration
        """
        return self.config.get('bot', {})
    
    def create_bot(self):
        """
        Create a Bot instance from the loaded configuration
        
        Returns:
            Configured Bot instance with all actions added
        """
        from rowdybottypiper.core.bot import Bot
        
        # Get bot configuration
        bot_config = self.get_bot_config()
        
        # Create bot with config parameters
        bot = Bot(
            name=bot_config.get('name', 'yaml-bot'),
            chrome_driver_path=bot_config.get('chrome_driver_path'),
            headless=bot_config.get('headless', False),
            correlation_id=bot_config.get('correlation_id'),
            debug=bot_config.get('debug', False)
        )
        
        # Load and add all actions
        actions = self.load_actions()
        for action in actions:
            bot.add_action(action)
        
        return bot
    
    @staticmethod
    def save_actions_to_yaml(actions: List[Action], output_path: str, bot_config: Dict[str, Any] = {}):
        """
        Save actions to a YAML file
        
        Args:
            actions: List of Action instances
            output_path: Path where YAML file should be saved
            bot_config: Optional bot configuration to include
        """
        from rowdybottypiper.config.action_registry import ACTION_TYPE_NAMES
        
        # Convert actions to dicts
        action_dicts = BotSerializer.actions_to_dict(actions)
        
        # Convert Pydantic type discriminators back to friendly names
        # e.g., 'LoginAction' -> 'login'
        for action_dict in action_dicts:
            action_type_class = type(actions[action_dicts.index(action_dict)])
            friendly_name = ACTION_TYPE_NAMES.get(action_type_class)
            if friendly_name:
                action_dict['type'] = friendly_name
        
        # Build full config structure
        config = {}
        if bot_config:
            config['bot'] = bot_config
        config['actions'] = action_dicts
        
        # Write to YAML file
        outpath = Path(output_path)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(outpath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)