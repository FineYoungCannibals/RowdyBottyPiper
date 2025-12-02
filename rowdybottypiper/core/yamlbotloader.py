"""
YAML Configuration Loader for RowdyBottyPiper
Allows users to define bot workflows in YAML format
"""

import yaml
import os
import re
from typing import Dict, Any, Optional
from pathlib import Path


class YAMLBotLoader:
    """Load bot configuration from YAML files"""
    
    # Map action types to their class names
    ACTION_REGISTRY = {
        'login': 'LoginAction',
        'navigate': 'NavigateAction',
        'click': 'ClickAction',
        'scrape': 'ScrapeAction',
        'download': 'DownloadAction',
        'download_multiple': 'DownloadMultipleAction',
        'submit_form': 'SubmitFormAction',
        'logout': 'LogoutAction',
        'alert': 'AlertAction',
    }
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize loader with either a file path or config dictionary
        
        Args:
            config_path: Path to YAML config file
            config_dict: Dictionary containing configuration
        """
        if config_path:
            self.config = self._load_yaml_file(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("Either config_path or config_dict must be provided")
        
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
    
    def _import_action_class(self, action_type: str):
        """
        Dynamically import action class based on type
        
        Args:
            action_type: Action type from YAML (e.g., 'login', 'click')
            
        Returns:
            Action class
        """
        class_name = self.ACTION_REGISTRY.get(action_type)
        if not class_name:
            raise ValueError(f"Unknown action type: {action_type}")
        
        # Import the action class
        module_name = f"rowdybottypiper.actions.{action_type}"
        try:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import {class_name} from {module_name}: {e}")
    
    def _create_action(self, action_config: Dict[str, Any]):
        """
        Create an action instance from config
        
        Args:
            action_config: Dictionary with action configuration
            
        Returns:
            Action instance
        """
        action_type = action_config.pop('type')
        action_class = self._import_action_class(action_type)
        
        # Filter out None values (allows omitting optional params in YAML)
        params = {k: v for k, v in action_config.items() if v is not None}
        
        # Create and return action instance
        return action_class(**params)
    
    def create_bot(self):
        """
        Create a Bot instance from the loaded configuration
        
        Returns:
            Configured Bot instance with all actions added
        """
        from rowdybottypiper.core.bot import Bot
        
        # Get bot configuration
        bot_config = self.config.get('bot', {})
        
        # Create bot with config parameters
        bot = Bot(
            name=bot_config.get('name', 'yaml-bot'),
            chrome_driver_path=bot_config.get('chrome_driver_path'),
            headless=bot_config.get('headless', False),
            correlation_id=bot_config.get('correlation_id'),
            debug=bot_config.get('debug', False)
        )
        
        # Add all actions
        actions = self.config.get('actions', [])
        for action_config in actions:
            # Make a copy to avoid modifying original
            action_config_copy = action_config.copy()
            action = self._create_action(action_config_copy)
            bot.add_action(action)
        
        return bot
    
    @classmethod
    def from_file(cls, config_path: Optional[str] = None):
        """
        Convenience method to load from file and create bot
        
        Args:
            config_path: Path to YAML config file. If None, uses default location.
            
        Returns:
            Configured Bot instance
        """
        if config_path is None:
            config_path = cls._get_default_config_path()
        
        loader = cls(config_path=config_path)
        return loader.create_bot()
    
    @staticmethod
    def _get_default_config_path() -> str:
        """
        Get default config path with Docker-friendly defaults
        
        Priority order:
        1. RRP_CONFIG_PATH environment variable
        2. /etc/rowdybottypiper/config.yaml (Docker/production)
        3. ./config.yaml (local development)
        
        Returns:
            Path to config file
        """
        # Check environment variable first
        env_path = os.getenv('RRP_CONFIG_PATH')
        if env_path:
            return env_path
        
        # Check Docker/production location
        docker_path = '/etc/rowdybottypiper/config.yaml'
        if os.path.exists(docker_path):
            return docker_path
        
        # Fall back to local development
        return './config.yaml'
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """
        Convenience method to load from dictionary and create bot
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configured Bot instance
        """
        loader = cls(config_dict=config_dict)
        return loader.create_bot()
    
    def get_slack_config(self) -> Optional[Dict[str, Any]]:
        """
        Get Slack notification configuration if present
        
        Returns:
            Slack config dict or None
        """
        return self.config.get('slack')


# Example usage convenience function
def load_bot_from_yaml(config_path: Optional[str] = None):
    """
    Simple function to load and return a bot from YAML
    
    Args:
        config_path: Path to YAML config file. If None, uses default location:
                     1. RRP_CONFIG_PATH environment variable
                     2. /etc/rowdybottypiper/config.yaml (Docker/production)
                     3. ./config.yaml (local development)
        
    Returns:
        Configured Bot instance ready to run
        
    Example:
        # With explicit path
        bot = load_bot_from_yaml("my_bot.yaml")
        bot.run()
        
        # With default path (checks env var, then Docker path, then local)
        bot = load_bot_from_yaml()
        bot.run()
        
        # In Docker with environment variable
        # docker run -e RRP_CONFIG_PATH=/app/config.yaml ...
        bot = load_bot_from_yaml()  # Uses RRP_CONFIG_PATH
        bot.run()
    """
    return YAMLBotLoader.from_file(config_path)