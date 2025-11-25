# RowdyBottyPiper



Here you go — a clean, professional **Markdown usage guide** for your `Bot` class suitable for GitHub docs.

You can paste this into:
`docs/bot.md` or `README.md` under a “Usage” section.

---

# `Bot` – Web Automation Bot Framework

*A flexible, stateful, Selenium-powered automation bot with structured logging and metrics.*

---

## 📘 Overview

The `Bot` class provides a composable framework for building **stateful web automation bots**.
It supports:

* Chrome automation (headless or full)
* Action chaining (`add_action`)
* Structured logging (JSON-friendly)
* Metrics collection across actions
* Shared `BotContext` object
* Session propagation to `requests.Session`

This enables advanced bots that continue running across multiple states, pages, and workflows.

---

## 🚀 Installation

```bash
pip install rowdybottypiper
```

Or from source:

```bash
pip install -e .
```

---

## 🧠 Key Concepts

### **BotContext**

A shared memory object passed to every action.

### **Action**

Your custom units of work.
Each must implement:

```python
def run(self, driver, context) -> bool:
    ...
```

### **Structured Logging**

Every log entry includes:

* correlation ID
* action name
* timestamps
* arbitrary structured data fields

### **BotMetrics**

Collects timing, failures, and action-level metrics.

---

## 🏗️ Creating a Bot Instance

```python
from rowdybottypiper.core.bot import Bot

bot = Bot(
    name="MyAutomationBot",
    headless=True,
    debug=True
)
```

### Optional Parameters

| Parameter            | Type      | Description                    |
| -------------------- | --------- | ------------------------------ |
| `name`               | `str`     | Human-readable bot name        |
| `chrome_driver_path` | `str`     | Path to custom ChromeDriver    |
| `headless`           | `bool`    | Run Chrome in headless mode    |
| `chrome_options`     | `Options` | Custom Selenium Chrome Options |
| `correlation_id`     | `str`     | For distributed tracing        |
| `debug`              | `bool`    | Enables verbose logging        |

---

## ➕ Adding Actions

```python
from my_actions.login import LoginAction
from my_actions.scrape import ScrapeAction

bot.add_action(LoginAction())
bot.add_action(ScrapeAction())
```

Actions are executed in the order added.

Each action gets:

* a Selenium driver
* the shared BotContext
* a logger
* its own metrics object

---

## ▶️ Running the Bot

```python
success = bot.run()

if success:
    print("Bot completed successfully!")
else:
    print("Bot failed.")
```

Internally, this performs:

1. Driver setup
2. Sequential execution of each action
3. Metrics aggregation
4. Structured logging
5. Driver teardown

---

## 🍪 Extracting Cookies

```python
cookies = bot.get_session_cookies()
print(cookies)
```

This returns a dictionary of all cookies from Selenium.

---

## 🌐 Creating a `requests` session from Selenium Cookies

```python
session = bot.create_requests_session()
response = session.get("https://example.com/api/profile")
print(response.json())
```

This allows seamless transition from browser automation → HTTP requests.

---

## 🛠 Example Action Implementation

```python
from rowdybottypiper.actions.action import Action

class LoginAction(Action):
    name = "Login"

    def run(self, driver, context):
        driver.get("https://example.com/login")
        driver.find_element(...).send_keys("user")
        driver.find_element(...).send_keys("pass")
        driver.find_element(...).click()
        
        # Save something in context
        context["is_logged_in"] = True

        return True
```

---

## 📊 Debug Mode

Pass `debug=True` to output:

* action list
* context at end
* metrics as structured logs

```python
bot = Bot("DebuggerBot", debug=True)
```

---

## ❗ Error Handling

If any action returns `False`, the bot:

* logs a structured error
* records metrics
* stops further execution
* tears down the driver

If any unhandled exception occurs:

* it is logged as a `critical` event
* metrics record failure
* bot shuts down cleanly

---

## 🧹 Driver Lifecycle

Handled automatically:

* `setup_driver()` on start
* `teardown_driver()` on exit

You do not need to manually manage Chrome sessions.

---

## 📦 API Reference

### `Bot.__init__()`

Initializes bot, logger, metrics, options.

### `add_action(action: Action)`

Adds an action to the workflow.

### `list_actions()`

Debug print of all actions.

### `run() -> bool`

Executes all actions in sequence.

### `setup_driver()`

Starts Chrome.

### `teardown_driver()`

Stops Chrome cleanly.

### `get_session_cookies() -> Dict[str, str]`

Returns all cookies as a dict.

### `create_requests_session() -> requests.Session`

Returns a `requests` session with Selenium cookies loaded.

---

If you want, I can also generate:

* a **full README.md** for the entire framework
* per-class documentation (Actions, Logger, Metrics, Context)
* Sphinx or mkdocs documentation
* UML class diagrams

Just send the next file when you're ready.
