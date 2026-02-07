"""
Bot runner for CLI execution
Handles running bots from various config sources
"""

import json
import sys
from pathlib import Path
from typing import Optional

from rowdybottypiper.config.action_loader import ActionLoader
from rowdybottypiper.config.bot_serializer import BotSerializer
from rowdybottypiper.core.bot import Bot


class BotRunner:
    """Run bots from different configuration sources"""
    
    @staticmethod
    def run_from_yaml(yaml_path: str, verbose: bool = False) -> bool:
        """
        Run bot from YAML configuration file
        
        Args:
            yaml_path: Path to YAML config file
            verbose: Enable verbose logging
            
        Returns:
            True if bot ran successfully, False otherwise
        """
        try:
            if verbose:
                print(f"Loading configuration from: {yaml_path}")
            
            loader = ActionLoader(yaml_path)
            bot = loader.create_bot()
            
            if verbose:
                actions = loader.load_actions()
                print(f"Loaded {len(actions)} actions")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.name} ({action.__class__.__name__})")
                print("\nStarting bot execution...\n")
            
            success = bot.run()
            
            if verbose:
                print(f"\nBot execution {'succeeded' if success else 'failed'}")
            
            return success
        
        except Exception as e:
            print(f"Error running bot from YAML: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    @staticmethod
    def run_from_json_file(json_path: str, bot_name: str = "json-bot", 
                          headless: bool = False, verbose: bool = False) -> bool:
        """
        Run bot from JSON configuration file
        
        Args:
            json_path: Path to JSON config file
            bot_name: Name for the bot instance
            headless: Run browser in headless mode
            verbose: Enable verbose logging
            
        Returns:
            True if bot ran successfully, False otherwise
        """
        try:
            if verbose:
                print(f"Loading configuration from: {json_path}")
            
            path = Path(json_path)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {json_path}")
            
            with open(path, 'r') as f:
                config = json.load(f)
            
            # Check if config includes bot settings or just actions
            if isinstance(config, dict) and 'actions' in config:
                actions_data = config['actions']
                bot_config = config.get('bot', {})
            else:
                # Assume it's just a list of actions
                actions_data = config
                bot_config = {}
            
            # Parse actions
            if isinstance(actions_data, dict):
                actions_data = [actions_data]
            
            actions = BotSerializer.dict_to_actions(actions_data)
            
            # Create bot
            bot = Bot(
                name=bot_config.get('name', bot_name),
                chrome_driver_path=bot_config.get('chrome_driver_path'),
                headless=bot_config.get('headless', headless),
                correlation_id=bot_config.get('correlation_id'),
                debug=bot_config.get('debug', verbose)
            )
            
            # Add actions
            for action in actions:
                bot.add_action(action)
            
            if verbose:
                print(f"Loaded {len(actions)} actions")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.name} ({action.__class__.__name__})")
                print("\nStarting bot execution...\n")
            
            success = bot.run()
            
            if verbose:
                print(f"\nBot execution {'succeeded' if success else 'failed'}")
            
            return success
        
        except Exception as e:
            print(f"Error running bot from JSON file: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    @staticmethod
    def run_from_json_string(json_str: str, bot_name: str = "json-bot",
                            headless: bool = False, verbose: bool = False) -> bool:
        """
        Run bot from JSON string configuration (e.g., from API/Urza)
        
        Args:
            json_str: JSON string containing action configurations
            bot_name: Name for the bot instance
            headless: Run browser in headless mode
            verbose: Enable verbose logging
            
        Returns:
            True if bot ran successfully, False otherwise
        """
        try:
            if verbose:
                print("Parsing JSON configuration...")
            
            config = json.loads(json_str)
            
            # Check if config includes bot settings or just actions
            if isinstance(config, dict) and 'actions' in config:
                actions_data = config['actions']
                bot_config = config.get('bot', {})
            else:
                # Assume it's just a list of actions
                actions_data = config
                bot_config = {}
            
            # Parse actions
            if isinstance(actions_data, dict):
                actions_data = [actions_data]
            
            actions = BotSerializer.dict_to_actions(actions_data)
            
            # Create bot
            bot = Bot(
                name=bot_config.get('name', bot_name),
                chrome_driver_path=bot_config.get('chrome_driver_path'),
                headless=bot_config.get('headless', headless),
                correlation_id=bot_config.get('correlation_id'),
                debug=bot_config.get('debug', verbose)
            )
            
            # Add actions
            for action in actions:
                bot.add_action(action)
            
            if verbose:
                print(f"Loaded {len(actions)} actions")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.name} ({action.__class__.__name__})")
                print("\nStarting bot execution...\n")
            
            success = bot.run()
            
            if verbose:
                print(f"\nBot execution {'succeeded' if success else 'failed'}")
            
            return success
        
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error running bot from JSON string: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return False


def run_bot(config: Optional[str] = None, 
           config_file: Optional[str] = None,
           bot_name: str = "cli-bot",
           headless: bool = False,
           verbose: bool = False) -> bool:
    """
    Main entry point for running bots from CLI
    
    Args:
        config: JSON string configuration
        config_file: Path to YAML or JSON config file
        bot_name: Name for the bot (used when creating from JSON string)
        headless: Run browser in headless mode
        verbose: Enable verbose logging
        
    Returns:
        True if bot ran successfully, False otherwise
    """
    runner = BotRunner()
    
    # Determine config source
    if config_file:
        path = Path(config_file)
        
        if not path.exists():
            print(f"Error: Config file not found: {config_file}", file=sys.stderr)
            return False
        
        # Determine file type by extension
        if path.suffix.lower() in ['.yaml', '.yml']:
            return runner.run_from_yaml(config_file, verbose=verbose)
        elif path.suffix.lower() == '.json':
            return runner.run_from_json_file(config_file, bot_name=bot_name, 
                                            headless=headless, verbose=verbose)
        else:
            print(f"Error: Unsupported file type: {path.suffix}", file=sys.stderr)
            print("Supported types: .yaml, .yml, .json", file=sys.stderr)
            return False
    
    elif config:
        # JSON string from command line or API
        return runner.run_from_json_string(config, bot_name=bot_name, 
                                          headless=headless, verbose=verbose)
    
    else:
        print("Error: Must provide either --config or --config-file", file=sys.stderr)
        return False