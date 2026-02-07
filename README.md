# RowdyBottyPiper (RBP)

A lightweight browser automation framework that lets you define workflows in JSON or YAML and execute them via CLI, API, or Telegram bot integration.

## What is RBP?

RowdyBottyPiper is a wrapper around [nodriver](https://github.com/ultrafunk/nodriver) that allows you to:
- Define browser automation tasks as simple JSON/YAML configs
- Execute workflows from the command line
- Integrate with external systems (like Urza) via JSON APIs
- Run automated tasks triggered by Telegram messages

**Design Philosophy:** Configuration over code. Define what you want done, not how to do it.

## Features

- 🎯 **Simple Action-Based System** - Navigate, click, fill forms, upload files
- 📝 **Config-Driven** - Define workflows in JSON or YAML
- 🤖 **Pydantic Models** - Automatic validation and serialization
- 🔄 **Built-in Retry Logic** - Configurable retries with delays
- 🎭 **Realistic Interactions** - Human-like typing and delays
- 🚀 **Async by Default** - Built on nodriver for modern async Python
- 🔌 **Integration Ready** - Easy to integrate with Telegram, APIs, or custom systems

## Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd RowdyBottyPiper

# Install dependencies
pip install -r requirements.txt

# Install Chrome (required)
# macOS:
brew install --cask google-chrome

# Ubuntu/Debian:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable
```

## Quick Start

### Run from JSON string:
```bash
python -m rowdybottypiper.cli.shell '[{"action_type": "browse", "url": "https://www.google.com"}]'
```

### Example: Login and Download Workflow
```json
[
  {
    "action_type": "browse",
    "url": "https://example.com/login"
  },
  {
    "action_type": "submit",
    "fields": [
      ["#username", "myuser"],
      ["#password", "mypass"]
    ],
    "element": "#login-btn"
  },
  {
    "action_type": "browse",
    "url": "https://example.com/downloads"
  },
  {
    "action_type": "click",
    "element": ".download-latest"
  }
]
```

Save as `workflow.json` and run:
```bash
python -m rowdybottypiper.cli.shell "$(cat workflow.json)"
```

## Available Actions

### Browse
Navigate to a URL.
```json
{
  "action_type": "browse",
  "url": "https://example.com"
}
```

### Click
Click an element.
```json
{
  "action_type": "click",
  "element": "#submit-button"
}
```

### Submit Form
Fill multiple fields and submit.
```json
{
  "action_type": "submit",
  "fields": [
    ["#email", "user@example.com"],
    ["#password", "secret123"]
  ],
  "element": "button[type='submit']"
}
```

### Upload File
Upload a file to an input element.
```json
{
  "action_type": "upload",
  "element": "input[type='file']",
  "file_path": "/path/to/file.pdf"
}
```

## Programmatic Usage
```python
import asyncio
from pydantic import TypeAdapter
from typing import List
from rowdybottypiper.bot.main import Bot, Action

# Define actions
config = [
    {"action_type": "browse", "url": "https://example.com"},
    {"action_type": "click", "element": "#my-button"}
]

# Parse and run
async def main():
    actions = TypeAdapter(List[Action]).validate_python(config)
    bot = Bot(actions)
    await bot.run()

asyncio.run(main())
```

## Telegram Integration

Create a Telegram bot listener to execute workflows on demand:
```python
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from pydantic import TypeAdapter
from typing import List
from rowdybottypiper.bot.main import Bot, Action

async def handle_message(update: Update, context):
    """Execute bot from JSON config sent via Telegram"""
    json_config = update.message.text
    
    try:
        actions = TypeAdapter(List[Action]).validate_json(json_config)
        bot = Bot(actions)
        
        await update.message.reply_text("🤖 Running bot...")
        await bot.run()
        await update.message.reply_text("✓ Task completed!")
    except Exception as e:
        await update.message.reply_text(f"✗ Error: {e}")

# Start listener
app = Application.builder().token("YOUR_TELEGRAM_TOKEN").build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.run_polling()
```

## Configuration

### Action Parameters

All actions support these base parameters:
```json
{
  "action_type": "click",
  "element": "#button",
  "retry_count": 3,
  "retry_delay": 2,
  "wait_lower": 1.1,
  "wait_upper": 10.0
}
```

- `retry_count`: Number of retry attempts (default: 3)
- `retry_delay`: Seconds between retries (default: 2)
- `wait_lower`: Minimum wait time in seconds (default: 1.1)
- `wait_upper`: Maximum wait time in seconds (default: 10.0)

### Realistic Interactions

RBP includes realistic typing with character-by-character delays to simulate human behavior:
```python
from rowdybottypiper.utils.realistic import slow_typing

# Types with random delays between characters
await slow_typing(element, "Hello World")
```

## Project Structure
```
rowdybottypiper/
├── actions/
│   └── base.py           # Action definitions (Browse, Click, Form, Upload)
├── bot/
│   └── main.py           # Bot orchestrator
├── cli/
│   └── shell.py          # CLI entry point
├── utils/
│   └── realistic.py      # Human-like interaction utilities
└── config/               # (Future) Config loaders for YAML/advanced features
```

## Use Cases

- **Scheduled Downloads** - Daily reports, invoices, statements
- **Form Automation** - Repetitive form submissions
- **Web Scraping** - Extract data from authenticated sites
- **Testing** - Automated browser testing
- **Integration** - Connect web UIs to your automation pipelines

## Why nodriver?

It's the successor to undetected-chrome, period.
RBP uses [nodriver](https://github.com/ultrafunk/nodriver) instead of Selenium because it:
- Uses Chrome DevTools Protocol directly (faster, more reliable)
- Harder to detect as automation (bypasses many anti-bot measures)
- Modern async/await patterns
- Lightweight and efficient

## Requirements

- Python 3.11+
- Chrome/Chromium browser
- nodriver
- pydantic

## Roadmap

- [ ] YAML config support
- [ ] Interactive shell (cmd2)
- [ ] More action types (wait, screenshot, execute_script)
- [ ] Better error handling and logging
- [ ] File download verification
- [ ] Context/state management between actions

## Contributing

Contributions welcome! This is a personal project but feel free to open issues or PRs.

## License

MIT License - do whatever you want with it.

## Credits

Built with:
- [nodriver](https://github.com/ultrafunk/nodriver) - Undetectable browser automation
- [pydantic](https://github.com/pydantic/pydantic) - Data validation

---

**RowdyBottyPiper** - Because sometimes you just need a bot that does what you tell it.