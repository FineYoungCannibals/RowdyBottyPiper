"""
Simple shell for testing RowdyBottyPiper
"""

import asyncio
import json
import sys
from pydantic import TypeAdapter
from typing import List

from rowdybottypiper.bot.main import Bot
from rowdybottypiper.bot.main import Action


async def main():
    if len(sys.argv) < 2:
        print("Usage: python shell.py '<json_string>'")
        sys.exit(1)
    
    json_string = sys.argv[1]
    
    try:
        # Parse JSON to actions
        action_adapter = TypeAdapter(List[Action])
        actions = action_adapter.validate_json(json_string)
        
        print(f"Loaded {len(actions)} action(s)")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action.action_type}")
        
        # Create and run bot
        bot = Bot(actions)
        await bot.run()
        
        print("\n✓ Bot execution completed")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())