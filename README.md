# RowdyBottyPiper

A flexible Python framework for building stateful web automation bots with comprehensive logging and metrics. Perfect for testing anti-bot detection systems, automated workflows, and Docker/K8s deployments. Run in the room with a chair, and start swinging it, bag-pipes in hand.

## 🎯 Features

- **Modular Action System**: Build complex workflows by chaining reusable actions
- **YAML Configuration**: Define workflows in simple YAML files (no Python required!)
- **Docker-First Deployment**: Auto-config discovery, one image for infinite bots
- **Session Management**: Maintain authentication state across multiple actions
- **Comprehensive Logging**: Structured JSON logs with correlation IDs for distributed systems
- **Built-in Metrics**: Track success rates, execution times, and retry attempts
- **Error Handling**: Automatic retries with configurable delays
- **Slack Integration**: Built-in notifications for bot completion/failure
- **K8s Ready**: Designed for horizontal scaling with proper logging and correlation
- **Custom ChromeDriver**: Support for custom drivers to test anti-bot detection
- **Context Sharing**: Pass data between actions seamlessly

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [YAML Configuration (New!)](#-yaml-configuration-new)
- [Docker Deployment (New!)](#-docker-deployment-new)
- [Core Concepts](#core-concepts)
- [Usage Examples](#usage-examples)
- [Built-in Actions](#built-in-actions)
- [Creating Custom Actions](#creating-custom-actions)
- [Logging and Metrics](#logging-and-metrics)
- [API Reference](#api-reference)

## 🚀 Installation
```bash
pip install rowdybottypiper
```
### Requirements

- Python > 3.8 && < 3.12
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)

### Warnings
The framework assumes you are taking care of networking upstream of the application running using this framework.

## ⚡ Quick Start

### Option 1: Python API (Traditional)

```python
from rowdybottypiper.core.bot import Bot
from rowdybottypiper.logging.config import setup_logging
from rowdybottypiper.actions.navigate import NavigateAction
from rowdybottypiper.actions.login import LoginAction
from rowdybottypiper.actions.click import ClickAction
from rowdybottypiper.actions.submitform import SubmitFormAction

# Configure logging
setup_logging(log_level="INFO", json_format=True)

# Create a bot
bot = Bot(
    name="MyFirstBot",
    chrome_driver_path="/path/to/chromedriver",  # Optional
    headless=False
)

# Add actions
bot.add_action(
    LoginAction(
        url="https://example.com/login",
        username="user@example.com",
        password="password123",
        username_selector="#email",
        password_selector="#password",
        submit_selector="button[type='submit']",
        success_indicator=".dashboard"
    )
).add_action(
    NavigateAction(url="https://example.com/products")
).add_action(
    ScrapeAction(
        selector=".product-name",
        context_key="products"
    )
)

# Run the bot
success = bot.run()

# Access scraped data
if success:
    products = bot.context.get('products', [])
    print(f"Scraped {len(products)} products: {products}")
```

### Option 2: YAML Configuration (New! 🎉)

**Create a config file** (`my_bot.yaml`):

```yaml
bot:
  name: "my-bot"
  headless: false

variables:
  base_url: "https://example.com"
  username: "${LOGIN_USERNAME}"
  password: "${LOGIN_PASSWORD}"

actions:
  - type: login
    url: "${base_url}/login"
    username: "${username}"
    password: "${password}"
    username_selector: "#email"
    password_selector: "#password"
    submit_selector: "button[type='submit']"
    success_indicator: ".dashboard"

  - type: navigate
    url: "${base_url}/products"

  - type: scrape
    selector: ".product-name"
    context_key: "products"

slack:
  notify_on_success: true
  success_message: "Bot completed successfully!"
```

**Run it:**

```python
from rowdybottypiper import load_bot_from_yaml

bot = load_bot_from_yaml("my_bot.yaml")
bot.run()
```

**Or with Docker:**

```bash
docker run -v ./my_bot.yaml:/etc/rowdybottypiper/config.yaml \
           -e LOGIN_USERNAME=user@example.com \
           -e LOGIN_PASSWORD=secret123 \
           rowdybottypiper:latest
```

## 🎨 YAML Configuration (New!)

Define your bot workflows in simple YAML files - no Python knowledge required!

### Key Features

- ✅ **Environment Variables**: `${VAR_NAME}` syntax for secrets
- ✅ **Reusable Variables**: Define once, use everywhere
- ✅ **All Actions Supported**: login, navigate, click, scrape, download, etc.
- ✅ **Slack Integration**: Built-in notification support
- ✅ **LLM-Friendly**: Perfect for AI-assisted workflow generation
- ✅ **Docker-Optimized**: Auto-discovers config at standard locations

### Simple Example

```yaml
bot:
  name: "product-scraper"
  headless: true

variables:
  site: "https://shop.example.com"
  user: "${SHOP_USERNAME}"
  pass: "${SHOP_PASSWORD}"

actions:
  - type: login
    url: "${site}/login"
    username: "${user}"
    password: "${pass}"
    username_selector: "#email"
    password_selector: "#password"
    submit_selector: "button"
    success_indicator: ".dashboard"

  - type: scrape
    selector: ".product-price"
    context_key: "prices"

slack:
  notify_on_success: true
  success_message: "Scraped ${prices.length} products!"
```

### Usage

```python
# Load from file
from rowdybottypiper import load_bot_from_yaml

bot = load_bot_from_yaml("config.yaml")
bot.run()

# Or let it auto-discover config
# Checks: RRP_CONFIG_PATH env var → /etc/rowdybottypiper/config.yaml → ./config.yaml
bot = load_bot_from_yaml()  # No path needed!
bot.run()
```

### 📖 Complete Documentation

- **[YAML Configuration Guide](docs/yaml_config.md)** - Complete reference for all action types, parameters, and examples
- **[Docker Deployment Guide](docs/docker_deployment.md)** - Full Docker deployment documentation
- **[Docker Quick Start](docs/docker_quick_start.md)** - TL;DR for Docker deployment

## 🐳 Docker Deployment (New!)

Deploy bots in Docker with automatic config discovery!

### Quick Start

**1. Create your config:**

```yaml
# my_bot.yaml
bot:
  name: "docker-bot"
  headless: true
actions:
  - type: navigate
    url: "https://example.com"
```

**2. Create docker-compose.yml:**

```yaml
version: '3.8'
services:
  bot:
    image: rowdybottypiper:latest
    volumes:
      # Auto-discovered at /etc/rowdybottypiper/config.yaml
      - ./my_bot.yaml:/etc/rowdybottypiper/config.yaml:ro
      - ./downloads:/app/downloads
    environment:
      - LOGIN_USERNAME=${USERNAME}
      - LOGIN_PASSWORD=${PASSWORD}
      - RRP_SLACK_BOT_TOKEN=${SLACK_TOKEN}
      - RRP_SLACK_CHANNEL=${SLACK_CHANNEL}
    restart: unless-stopped
```

**3. Deploy:**

```bash
docker-compose up -d
```

### Multiple Bots, One Image

```yaml
version: '3.8'
services:
  scraper1:
    image: rowdybottypiper:latest
    volumes:
      - ./configs/scraper1.yaml:/etc/rowdybottypiper/config.yaml:ro
    environment:
      - RRP_SLACK_CHANNEL=C111111
  
  scraper2:
    image: rowdybottypiper:latest
    volumes:
      - ./configs/scraper2.yaml:/etc/rowdybottypiper/config.yaml:ro
    environment:
      - RRP_SLACK_CHANNEL=C222222
```

Each bot automatically discovers its own config!

### Config Path Auto-Discovery

The bot looks for config in this order:

1. `RRP_CONFIG_PATH` environment variable
2. `/etc/rowdybottypiper/config.yaml` (Docker standard)
3. `./config.yaml` (local development)

**No hardcoded paths needed!**

### 📖 Complete Documentation

- **[Docker Deployment Guide](docs/docker_deployment.md)** - Complete guide with examples, monitoring, troubleshooting
- **[Docker Quick Start](docs/docker_quick_start.md)** - Quick reference for common patterns

## 🧠 Core Concepts

### Bot

The `Bot` class is the main orchestrator. It:
- Manages the ChromeDriver lifecycle
- Executes actions in sequence
- Tracks metrics and logs
- Maintains shared context
- Handles Slack notifications (if configured)

### Action

Actions are discrete steps in your workflow. Each action:
- Has a name for identification
- Can access and modify shared context
- Has built-in retry logic
- Reports metrics (duration, attempts, status)
- Inherits from the `Action` base class
- Available types: Login, Navigate, Click, Scrape, Download, SubmitForm, and more

### Context

The `BotContext` is a shared state object that allows actions to:
- Store data for later actions (e.g., scraped content, tokens)
- Share cookies and headers
- Track session state

### Metrics

Both bots and actions automatically track:
- Execution duration
- Success/failure status
- Retry attempts
- Error messages

### Slack Integration

Bots can automatically send Slack notifications:

**Setup** (environment variables):
```bash
export RRP_SLACK_BOT_TOKEN="xoxb-your-token"
export RRP_SLACK_CHANNEL="C1234567890"
```

**Usage** (automatic if env vars set):
```python
bot = Bot("my-bot")
# Slack client auto-configured if env vars present
bot.run()

# Or send custom notifications
if bot.slack:
    bot.notify_slack(
        title="Custom Alert",
        message="Something important happened!",
        file_path="report.pdf"  # Optional file attachment
    )
```

**YAML Configuration:**
```yaml
slack:
  notify_on_success: true
  notify_on_failure: true
  success_message: "Bot completed!"
  failure_message: "Bot failed - check logs"
```

## 💡 Usage Examples

### Example 1: E-commerce Scraper

```yaml
bot:
  name: "price-monitor"
  headless: true

variables:
  shop_url: "https://shop.example.com"

actions:
  - type: navigate
    url: "${shop_url}/products/laptops"

  - type: scrape
    selector: ".product-name"
    context_key: "product_names"

  - type: scrape
    selector: ".product-price"
    context_key: "product_prices"
    attribute: "data-price"

  - type: download
    selector: ".download-catalog"
    download_dir: "./catalogs"
    expected_filename: "*.pdf"

slack:
  notify_on_success: true
  success_message: "Scraped ${product_names.length} products"
```

### Example 2: Report Downloader

```python
from rowdybottypiper import load_bot_from_yaml

# Load bot from YAML
bot = load_bot_from_yaml("report_bot.yaml")

# Run bot
success = bot.run()

# Access downloaded files
if success:
    downloads = bot.context.get('downloads', [])
    for download in downloads:
        print(f"Downloaded: {download['filename']}")
        print(f"Size: {download['size_bytes']} bytes")
```

### Example 3: Custom Script with YAML

```python
from rowdybottypiper import load_bot_from_yaml
import sys

def main():
    # Load config (auto-discovers from env or default locations)
    bot = load_bot_from_yaml()
    
    # Run bot
    success = bot.run()
    
    # Custom post-processing
    if success:
        data = bot.context.get('scraped_data', [])
        
        # Send custom Slack notification
        if bot.slack:
            bot.notify_slack(
                title="Daily Report",
                message=f"Processed {len(data)} items",
                file_path="results.csv"
            )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

### Testing Anti-Bot Detection

Undetected ChromeDriver (UC) ships as a requirement with this package. Depending on your operating system, by default, UC's binary can be found in one of two places:

```bash
ls ~/.local/share/undetected_chromedriver/<hash>_chromdriver
```

```
file C:\Users\<YOURUSERNAME>\AppData\Roaming\undetected_chromedriver\<hash>_chromedriver.exe
```

Based on that pathing you might then pass options and specific drivers to the Bot framework thusly:

```python
from rowdybottypiper import Bot
from selenium.webdriver.chrome.options import Options

# Configure Chrome options to mimic real browser
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

bot = Bot(
    name="DetectionTest",
    chrome_driver_path="/path/to/custom/chromedriver",
    chrome_options=chrome_options,
    headless=False
)

# Add actions to test detection...
bot.run()
```

## 🔧 Built-in Actions

### LoginAction

Handles authentication flows.

```python
LoginAction(
    url="https://site.com/login",
    username="user@example.com",
    password="password123",
    username_selector="#email",
    password_selector="#password",
    submit_selector="button[type='submit']",
    success_indicator=".dashboard"  # Optional: verify login success
)
```

**YAML:**
```yaml
- type: login
  url: "https://site.com/login"
  username: "${USERNAME}"
  password: "${PASSWORD}"
  username_selector: "#email"
  password_selector: "#password"
  submit_selector: "button[type='submit']"
  success_indicator: ".dashboard"
```

### NavigateAction

Navigate to a URL.

```python
NavigateAction(
    url="https://site.com/page",
    wait_time=2  # Seconds to wait after navigation
)
```

**YAML:**
```yaml
- type: navigate
  url: "https://site.com/page"
  wait_time: 2
```

### ClickAction

Click an element on the page.

```python
ClickAction(
    selector=".button-class",
    by="CSS_SELECTOR",  # or "XPATH", "ID", "CLASS_NAME"
    wait_time=2
)
```

**YAML:**
```yaml
- type: click
  selector: ".button-class"
  by: "CSS_SELECTOR"
  wait_time: 2
```

### ScrapeAction

Extract data from the page.

```python
ScrapeAction(
    selector=".data-item",
    context_key="scraped_items",  # Key to store in context
    attribute=None  # Optional: extract attribute instead of text
)
```

**YAML:**
```yaml
- type: scrape
  selector: ".data-item"
  context_key: "scraped_items"
  attribute: "data-id"  # Optional
```

### DownloadAction

Download files from the page.

```python
DownloadAction(
    selector=".download-button",
    download_dir="./downloads",
    expected_filename="*.pdf",
    timeout=60,
    verify_download=True
)
```

**YAML:**
```yaml
- type: download
  selector: ".download-button"
  download_dir: "./downloads"
  expected_filename: "*.pdf"
  timeout: 60
```

### SubmitFormAction

Fill and submit forms.

```python
SubmitFormAction(
    form_fields=[
        ('#firstname', 'John', 'text'),
        ('#lastname', 'Doe', 'text'),
        ('#email', 'john@example.com', 'email'),
        ('#country', 'United States', 'select'),
        ('#terms', 'true', 'checkbox')
    ],
    submit_selector='button[type="submit"]',
    success_indicator='.success-message'
)
```

### LogoutAction

Handle logout.

```python
LogoutAction(
    logout_url="https://site.com/logout",  # Option 1: direct URL
    logout_selector=".logout-btn"  # Option 2: click element
)
```

**See [YAML Configuration Guide](docs/yaml_config.md) for complete action reference.**

## 🛠️ Creating Custom Actions

Extend the `Action` base class to create custom actions:

```python
from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from selenium import webdriver
from selenium.webdriver.common.by import By

class CustomAction(Action):
    """Custom action example"""
    
    def __init__(self, param1: str, param2: int):
        super().__init__(name="CustomAction", retry_count=3)
        self.param1 = param1
        self.param2 = param2
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        """
        Execute the action
        Returns True if successful, False otherwise
        """
        try:
            # Your custom logic here
            element = driver.find_element(By.CSS_SELECTOR, self.param1)
            
            if self.logger:
                self.logger.info(f"Processing {self.param1}")
            
            # Store results in context
            context.set('custom_result', element.text)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed: {str(e)}")
            return False

# Use your custom action
bot = Bot(name="CustomBot")
bot.add_action(CustomAction(param1=".selector", param2=5))
bot.run()
```

### Custom Action Best Practices

1. **Always call `super().__init__()`** with a descriptive name
2. **Return `True` for success**, `False` for failure
3. **Use `self.logger`** for structured logging (if available)
4. **Store important data** in context for subsequent actions
5. **Handle exceptions** gracefully
6. **Use `context.get()`** to access data from previous actions

## 📊 Logging and Metrics

### Structured Logging

All logs are JSON-formatted for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "correlation_id": "bot-run-12345",
  "logger_name": "Bot.MyBot",
  "level": "INFO",
  "message": "Action 'Login' completed successfully",
  "action": "Login",
  "duration": 2.341,
  "attempts": 1
}
```

### Configure Logging

```python
from rowdybottypiper.logging.config import setup_logging

# For development (console output)
setup_logging(log_level="DEBUG", json_format=False)

# For production/K8s (JSON to stdout)
setup_logging(log_level="INFO", json_format=True)

# With file output
setup_logging(
    log_level="INFO",
    json_format=True,
    log_to_file=True,
    log_file_path="/var/log/bots/execution.log"
)
```

### Access Metrics

```python
bot = Bot(name="MetricsExample")
# ... add actions ...
bot.run()

# Get full metrics
metrics = bot.metrics.to_dict()

print(f"Bot: {metrics['bot_name']}")
print(f"Duration: {metrics['duration_seconds']}s")
print(f"Success: {metrics['overall_success']}")
print(f"Success Rate: {metrics['success_rate']}%")
print(f"Total Actions: {metrics['total_actions']}")
print(f"Failed Actions: {metrics['failed_actions']}")

# Per-action metrics
for action in metrics['actions']:
    print(f"Action: {action['action_name']}")
    print(f"  Status: {action['status']}")
    print(f"  Duration: {action['duration_seconds']}s")
    print(f"  Attempts: {action['attempts']}")
```

## 📖 API Reference

### Bot Class

```python
Bot(
    name: str,
    chrome_driver_path: Optional[str] = None,
    headless: bool = False,
    chrome_options: Optional[Options] = None,
    correlation_id: Optional[str] = None,
    debug: bool = False
)
```

**Methods:**
- `add_action(action: Action) -> Bot`: Add an action (chainable)
- `run() -> bool`: Execute the bot workflow
- `notify_slack(title: str, message: str, file_path: Optional[str]) -> bool`: Send Slack notification
- `get_session_cookies() -> Dict[str, str]`: Get cookies from Selenium
- `create_requests_session() -> requests.Session`: Create requests session with cookies

**Attributes:**
- `context`: BotContext instance for shared data
- `metrics`: BotMetrics instance with execution data
- `logger`: StructuredLogger instance
- `correlation_id`: Unique ID for this bot run
- `slack`: SlackClient instance (if configured)

### YAML Loader

```python
from rowdybottypiper import load_bot_from_yaml, YAMLBotLoader

# Simple usage
bot = load_bot_from_yaml("config.yaml")

# Auto-discovery (checks RRP_CONFIG_PATH → /etc/rowdybottypiper/config.yaml → ./config.yaml)
bot = load_bot_from_yaml()

# Advanced usage
loader = YAMLBotLoader(config_path="config.yaml")
bot = loader.create_bot()
slack_config = loader.get_slack_config()
```

### Action Class

```python
Action(
    name: str,
    retry_count: int = 3,
    retry_delay: int = 2
)
```

**Methods to Implement:**
- `execute(driver: webdriver.Chrome, context: BotContext) -> bool`: Main action logic

**Available Attributes:**
- `self.logger`: StructuredLogger (may be None)
- `self.metrics`: ActionMetrics instance
- `self.name`: Action name
- `self.retry_count`: Number of retry attempts
- `self.retry_delay`: Delay between retries (seconds)

### BotContext Class

```python
context = BotContext()
```

**Methods:**
- `set(key: str, value: Any)`: Store data
- `get(key: str, default=None) -> Any`: Retrieve data
- `update(data: Dict[str, Any])`: Update with multiple values

**Attributes:**
- `data`: Dict of stored values
- `cookies`: Dict of cookies
- `headers`: Dict of headers
- `session_active`: Boolean session state

## 🤝 Contributing

Project not currently open sourced for contribution.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### ChromeDriver Issues

**Problem**: `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solution**: Either:
1. Install ChromeDriver and add to PATH
2. Specify path explicitly: `Bot(chrome_driver_path="/path/to/chromedriver")`

### Headless Mode Issues

**Problem**: Bot works normally but fails in headless mode

**Solution**: Some sites detect headless Chrome. Try:
```python
chrome_options = Options()
chrome_options.add_argument('--headless=new')  # Use new headless mode
chrome_options.add_argument('--window-size=1920,1080')
bot = Bot(chrome_options=chrome_options)
```

**In Docker**: Always use `headless: true` in YAML config

### Config Not Found (Docker)

**Problem**: `FileNotFoundError: Config file not found`

**Solution**: Check mount path:
```bash
docker-compose exec bot ls -la /etc/rowdybottypiper/
```

Ensure config is mounted:
```yaml
volumes:
  - ./my_bot.yaml:/etc/rowdybottypiper/config.yaml:ro
```

### Environment Variables Not Working

**Problem**: Config has empty values where variables should be

**Solution**: 
1. Check `.env` file exists
2. Verify variables in docker-compose:
```bash
docker-compose config
```
3. Export before running:
```bash
export LOGIN_USERNAME=user@example.com
```

### Memory Issues in Docker

**Problem**: Pods getting OOMKilled

**Solution**: Chrome can be memory-hungry. Increase limits:
```yaml
services:
  bot:
    deploy:
      resources:
        limits:
          memory: "2Gi"
```

And ensure Chrome flags are set (automatically included in provided Dockerfile):
```yaml
bot:
  headless: true  # Required in Docker
```

### Slack Notifications Not Working

**Problem**: Bot runs but no Slack notifications

**Solution**:
1. Check environment variables are set:
```bash
echo $RRP_SLACK_BOT_TOKEN
echo $RRP_SLACK_CHANNEL
```

2. Verify bot is invited to channel:
```
/invite @YourBotName
```

3. Check bot logs for Slack initialization:
```bash
docker-compose logs bot | grep -i slack
```

## 📚 Additional Resources

- **[YAML Configuration Guide](docs/yaml_config.md)** - Complete YAML reference
- **[Docker Deployment Guide](docs/docker_deployment.md)** - Full Docker documentation
- **[Docker Quick Start](docs/docker_quick_start.md)** - Quick Docker reference
- **[Integration Guide](docs/integration_guide.md)** - Adding YAML support to your project

## 🎉 What's New in v1.4.0

- ✅ **YAML Configuration Support** - Define workflows without Python code
- ✅ **Docker-First Deployment** - Auto-config discovery at `/etc/rowdybottypiper/config.yaml`
- ✅ **Slack Integration** - Built-in notification support
- ✅ **Environment Variables** - `${VAR_NAME}` syntax in YAML configs
- ✅ **Multiple Deployment Patterns** - Examples for common use cases
- ✅ **LLM-Friendly** - Perfect for AI-assisted workflow generation

---

**Built with ❤️ for automation engineers who need reliable, scalable bot frameworks.**