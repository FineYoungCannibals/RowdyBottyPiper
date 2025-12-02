# RowdyBottyPiper

A flexible Python framework for building stateful web automation bots with comprehensive logging and metrics. Perfect for testing anti-bot detection systems, automated workflows, and K8s deployments. Run in the room with a chair, and start swinging it, bag-pipes in hand.

## 🎯 Features

- **Modular Action System**: Build complex workflows by chaining reusable actions
- **Session Management**: Maintain authentication state across multiple actions
- **Comprehensive Logging**: Structured JSON logs with correlation IDs for distributed systems
- **Built-in Metrics**: Track success rates, execution times, and retry attempts
- **Error Handling**: Automatic retries with configurable delays
- **K8s Ready**: Designed for horizontal scaling with proper logging and correlation
- **Custom ChromeDriver**: Support for custom drivers to test anti-bot detection
- **Context Sharing**: Pass data between actions seamlessly

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Usage Examples](#usage-examples)
- [Built-in Actions](#built-in-actions)
- [Creating Custom Actions](#creating-custom-actions)
- [Logging and Metrics](#logging-and-metrics)
- [K8s Deployment](#k8s-deployment)
- [API Reference](#api-reference)

## 🚀 Installation
```bash
pip install rowdybottypiper
```
### Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)

### Warnings
The framework assumes you are taking care of networking upstream of the application running using this framework.

## ⚡ Quick Start

Here's a simple example to get you started:

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
    SubmitFormAction(
        form_fields=[
            ('#firstname','Ivan','text'),
            ('#lastname','Ivanovich','text'),
            ('#email','ivan.ivanovich@proton.mail','email'),
            ('#country','Russian Federation','select'),
            ('#message','this is my message','textarea'),
            ('#newsletter','true','checkbox'),
            ('#terms','true','checkbox')
        ],
        submit_selector='button[type="submit"]',
        success_indicator='.success-message'
    )
).add_action(
    ScrapeAction(
        selector=".product-name",
        context_key="products"
    )
).add_action(
    LogoutAction(logout_selector=".logout-btn")
)

# Run the bot
success = bot.run()

# Access scraped data
if success:
    products = bot.context.get('products', [])
    print(f"Scraped {len(products)} products: {products}")
    
    # View metrics
    metrics = bot.metrics.to_dict()
    print(f"Execution took {metrics['duration_seconds']} seconds")
    print(f"Success rate: {metrics['success_rate']}%")
```

## 🧠 Core Concepts

### Bot

The `Bot` class is the main orchestrator. It:
- Manages the ChromeDriver lifecycle
- Executes actions in sequence
- Tracks metrics and logs
- Maintains shared context

### Action

Actions are discrete steps in your workflow. Each action:
- Has a name for identification
- Can access and modify shared context
- Has built-in retry logic
- Reports metrics (duration, attempts, status)
- Inherits from the `Action` base class
- Action types exist for Login, Form Submission, Downloading, Clicking, Reading, and handling Alerts/Pop-ups.

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

### NavigateAction

Navigate to a URL.

```python
NavigateAction(
    url="https://site.com/page",
    wait_time=2  # Seconds to wait after navigation
)
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

### ScrapeAction

Extract data from the page.

```python
ScrapeAction(
    selector=".data-item",
    context_key="scraped_items",  # Key to store in context
    attribute=None  # Optional: extract attribute instead of text
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

## 🛠️ Creating Custom Actions

Extend the `Action` base class to create custom actions:

```python
from rowdybottypiper.core import Action, BotContext
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class FillFormAction(Action):
    """Custom action to fill a form"""
    
    def __init__(self, form_data: dict):
        super().__init__(name="FillForm", retry_count=2)
        self.form_data = form_data
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        """
        Execute the action
        Returns True if successful, False otherwise
        """
        try:
            for field_name, value in self.form_data.items():
                field = driver.find_element(By.NAME, field_name)
                field.clear()
                field.send_keys(value)
                
                if self.logger:
                    self.logger.info(
                        f"Filled field '{field_name}'",
                        field=field_name
                    )
            
            # Store form data in context for later use
            context.set('form_submitted', True)
            context.set('form_data', self.form_data)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to fill form: {str(e)}")
            return False

# Use your custom action
bot = Bot(name="CustomBot")
bot.add_action(
    FillFormAction(form_data={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    })
)
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
from rowdybottypiper import setup_logging

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



### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

WORKDIR /app

# Install bot framework
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

# Run bot
CMD ["python", "k8s_bot.py"]
```

## 📖 API Reference

### Bot Class

```python
Bot(
    name: str,
    chrome_driver_path: Optional[str] = None,
    headless: bool = False,
    chrome_options: Optional[Options] = None,
    correlation_id: Optional[str] = None
)
```

**Methods:**
- `add_action(action: Action) -> Bot`: Add an action (chainable)
- `run() -> bool`: Execute the bot workflow
- `get_session_cookies() -> Dict[str, str]`: Get cookies from Selenium
- `create_requests_session() -> requests.Session`: Create requests session with cookies

**Attributes:**
- `context`: BotContext instance for shared data
- `metrics`: BotMetrics instance with execution data
- `logger`: StructuredLogger instance
- `correlation_id`: Unique ID for this bot run

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

### Memory Issues 

**Problem**: Pods getting OOMKilled

**Solution**: Chrome can be memory-hungry. Increase limits:
```yaml
resources:
  limits:
    memory: "2Gi"  # Increase from 1Gi
```

And add Chrome flags:
```python
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
```
