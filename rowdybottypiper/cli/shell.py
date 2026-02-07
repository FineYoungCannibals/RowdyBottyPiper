"""
Interactive shell for building and testing bot configurations
Uses cmd2 for rich command-line interface
"""

import cmd2
import json
from pathlib import Path
from typing import Optional, List

from rowdybottypiper.actions.action import Action
from rowdybottypiper.config.action_loader import ActionLoader
from rowdybottypiper.config.bot_serializer import BotSerializer
from rowdybottypiper.config.action_registry import ACTION_REGISTRY
from rowdybottypiper.core.bot import Bot


class InteractiveShell(cmd2.Cmd):
    """Interactive shell for RowdyBottyPiper bot configuration"""
    
    intro = """
╔══════════════════════════════════════════════════════════╗
║  RowdyBottyPiper Interactive Shell                       ║
║  Type 'help' for available commands                      ║
╚══════════════════════════════════════════════════════════╝
    """
    
    prompt = "(rbp) "
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # State
        self.actions: List[Action] = []
        self.bot_config: dict = {
            'name': 'interactive-bot',
            'headless': False,
            'debug': False
        }
        self.config_file: Optional[str] = None
        
        # Disable built-in commands we don't need
        self.hidden_commands.extend(['alias', 'edit', 'macro', 'run_pyscript', 'run_script'])
    
    # ========== Configuration Loading ==========
    
    def do_load(self, args):
        """
        Load configuration from a file
        
        Usage: load <filepath>
        
        Supports YAML and JSON files.
        """
        if not args:
            self.perror("Error: Please provide a file path")
            return
        
        filepath = args.strip()
        path = Path(filepath)
        
        if not path.exists():
            self.perror(f"Error: File not found: {filepath}")
            return
        
        try:
            if path.suffix.lower() in ['.yaml', '.yml']:
                loader = ActionLoader(filepath)
                self.actions = loader.load_actions()
                self.bot_config = loader.get_bot_config()
                self.config_file = filepath
                self.poutput(f"✓ Loaded {len(self.actions)} actions from {filepath}")
            
            elif path.suffix.lower() == '.json':
                with open(path, 'r') as f:
                    config = json.load(f)
                
                if isinstance(config, dict) and 'actions' in config:
                    actions_data = config['actions']
                    self.bot_config = config.get('bot', self.bot_config)
                else:
                    actions_data = config
                
                if isinstance(actions_data, dict):
                    actions_data = [actions_data]
                
                self.actions = BotSerializer.dict_to_actions(actions_data)
                self.config_file = filepath
                self.poutput(f"✓ Loaded {len(self.actions)} actions from {filepath}")
            
            else:
                self.perror(f"Error: Unsupported file type: {path.suffix}")
                self.poutput("Supported types: .yaml, .yml, .json")
        
        except Exception as e:
            self.perror(f"Error loading file: {e}")
    
    # ========== Viewing Configuration ==========
    
    def do_show(self, args):
        """
        Show current configuration
        
        Usage: 
            show actions    - Show all loaded actions
            show bot        - Show bot configuration
            show action <n> - Show details of action number n
        """
        args = args.strip().split()
        
        if not args or args[0] == 'actions':
            if not self.actions:
                self.poutput("No actions loaded")
                return
            
            self.poutput(f"\nLoaded Actions ({len(self.actions)}):")
            self.poutput("=" * 60)
            for i, action in enumerate(self.actions, 1):
                self.poutput(f"{i}. {action.name} ({action.__class__.__name__})")
            self.poutput("")
        
        elif args[0] == 'bot':
            self.poutput("\nBot Configuration:")
            self.poutput("=" * 60)
            for key, value in self.bot_config.items():
                self.poutput(f"{key}: {value}")
            self.poutput("")
        
        elif args[0] == 'action':
            if len(args) < 2:
                self.perror("Error: Please specify action number")
                return
            
            try:
                index = int(args[1]) - 1
                if index < 0 or index >= len(self.actions):
                    self.perror(f"Error: Action number must be between 1 and {len(self.actions)}")
                    return
                
                action = self.actions[index]
                self.poutput(f"\nAction {index + 1}: {action.name}")
                self.poutput("=" * 60)
                self.poutput(json.dumps(action.model_dump(), indent=2))
                self.poutput("")
            
            except ValueError:
                self.perror("Error: Action number must be an integer")
        
        else:
            self.perror(f"Error: Unknown show target: {args[0]}")
            self.poutput("Usage: show [actions|bot|action <n>]")
    
    # ========== Exporting Configuration ==========
    
    def do_export(self, args):
        """
        Export configuration to different formats
        
        Usage:
            export json           - Print actions as JSON string
            export json <file>    - Save actions as JSON file
            export yaml <file>    - Save actions as YAML file
        """
        if not self.actions:
            self.perror("Error: No actions loaded")
            return
        
        args = args.strip().split(maxsplit=1)
        
        if not args:
            self.perror("Error: Please specify export format (json or yaml)")
            return
        
        format_type = args[0].lower()
        
        if format_type == 'json':
            json_str = BotSerializer.actions_to_json(self.actions, indent=2)
            
            if len(args) > 1:
                # Save to file
                filepath = args[1]
                try:
                    with open(filepath, 'w') as f:
                        f.write(json_str)
                    self.poutput(f"✓ Exported to {filepath}")
                except Exception as e:
                    self.perror(f"Error saving file: {e}")
            else:
                # Print to console
                self.poutput("\nJSON Configuration:")
                self.poutput("=" * 60)
                self.poutput(json_str)
                self.poutput("")
        
        elif format_type == 'yaml':
            if len(args) < 2:
                self.perror("Error: Please specify output file path")
                return
            
            filepath = args[1]
            try:
                ActionLoader.save_actions_to_yaml(self.actions, filepath, self.bot_config)
                self.poutput(f"✓ Exported to {filepath}")
            except Exception as e:
                self.perror(f"Error saving YAML: {e}")
        
        else:
            self.perror(f"Error: Unknown format: {format_type}")
            self.poutput("Supported formats: json, yaml")
    
    # ========== Importing Configuration ==========
    
    def do_import_json(self, args):
        """
        Import actions from JSON string
        
        Usage: import <json_string>
        
        Example:
            import {"type": "NavigateAction", "name": "go_home", "url": "https://example.com"}
        """
        if not args:
            self.perror("Error: Please provide JSON string")
            return
        
        try:
            actions = BotSerializer.json_to_actions(args)
            self.actions.extend(actions)
            self.poutput(f"✓ Imported {len(actions)} action(s)")
        except Exception as e:
            self.perror(f"Error importing JSON: {e}")
    
    # ========== Validation ==========
    
    def do_validate(self, args):
        """
        Validate current configuration
        
        Usage: validate
        """
        if not self.actions:
            self.perror("Error: No actions to validate")
            return
        
        self.poutput("Validating configuration...")
        
        errors = []
        for i, action in enumerate(self.actions, 1):
            try:
                # Pydantic models are already validated on creation
                # But we can do additional checks here
                if not action.name:
                    errors.append(f"Action {i}: Missing name")
            except Exception as e:
                errors.append(f"Action {i}: {e}")
        
        if errors:
            self.perror(f"✗ Validation failed with {len(errors)} error(s):")
            for error in errors:
                self.perror(f"  - {error}")
        else:
            self.poutput(f"✓ Configuration valid ({len(self.actions)} actions)")
    
    # ========== Bot Execution ==========
    
    def do_run(self, args):
        """
        Run the bot with current configuration
        
        Usage: run [--headless] [--debug]
        """
        if not self.actions:
            self.perror("Error: No actions loaded")
            return
        
        # Parse flags
        headless = '--headless' in args
        debug = '--debug' in args
        
        try:
            self.poutput(f"\nRunning bot with {len(self.actions)} actions...")
            
            # Create bot
            bot = Bot(
                name=self.bot_config.get('name', 'interactive-bot'),
                chrome_driver_path=self.bot_config.get('chrome_driver_path'),
                headless=headless or self.bot_config.get('headless', False),
                correlation_id=self.bot_config.get('correlation_id'),
                debug=debug or self.bot_config.get('debug', False)
            )
            
            # Add actions
            for action in self.actions:
                bot.add_action(action)
            
            # Run
            success = bot.run()
            
            if success:
                self.poutput("\n✓ Bot execution succeeded")
            else:
                self.perror("\n✗ Bot execution failed")
        
        except Exception as e:
            self.perror(f"Error running bot: {e}")
    
    # ========== Action Management ==========
    
    def do_clear(self, args):
        """
        Clear all loaded actions
        
        Usage: clear
        """
        if self.actions:
            count = len(self.actions)
            self.actions = []
            self.poutput(f"✓ Cleared {count} action(s)")
        else:
            self.poutput("No actions to clear")
    
    def do_remove(self, args):
        """
        Remove an action by number
        
        Usage: remove <action_number>
        """
        if not args:
            self.perror("Error: Please specify action number")
            return
        
        try:
            index = int(args.strip()) - 1
            if index < 0 or index >= len(self.actions):
                self.perror(f"Error: Action number must be between 1 and {len(self.actions)}")
                return
            
            removed = self.actions.pop(index)
            self.poutput(f"✓ Removed action: {removed.name}")
        
        except ValueError:
            self.perror("Error: Action number must be an integer")
    
    # ========== Information ==========
    
    def do_types(self, args):
        """
        Show available action types
        
        Usage: types
        """
        self.poutput("\nAvailable Action Types:")
        self.poutput("=" * 60)
        for action_type in sorted(ACTION_REGISTRY.keys()):
            action_class = ACTION_REGISTRY[action_type]
            self.poutput(f"  {action_type:<20} -> {action_class.__name__}")
        self.poutput("")
    
    def do_exit(self, args):
        """Exit the shell"""
        self.poutput("Goodbye!")
        return True
    
    # Aliases
    do_quit = do_exit
    do_EOF = do_exit


def start_interactive_shell():
    """Start the interactive shell"""
    shell = InteractiveShell()
    shell.cmdloop()