from bot_framework.core.bot import Bot
from bot_framework.actions.login import LoginAction
from bot_framework.actions.navigate import NavigateAction
from bot_framework.actions.scrape import ScrapeAction
from bot_framework.actions.click import ClickAction
from bot_framework.actions.logout import LogoutAction
from bot_framework.logging.structured_logger import setup_logging
import json
import datetime


setup_logging(log_level="INFO", json_format=True)

# Create a bot with custom chrome driver
bot = Bot(
    name="ExampleBot",
    chrome_driver_path="/path/to/your/chromedriver",
    headless=False,
    correlation_id=f"test-run-{datetime.datetime.now().strftime('%s')}"  # Optional: useful for tracking in K8s
)

# Chain actions together
bot.add_action(
    LoginAction(
        url="https://example.com/login",
        username="your_username",
        password="your_password",
        username_selector="input[name='username']",
        password_selector="input[name='password']",
        submit_selector="button[type='submit']",
        success_indicator=".dashboard"
    )
).add_action(
    NavigateAction(url="https://example.com/dashboard")
).add_action(
    ScrapeAction(
        selector=".item-title",
        context_key="items"
    )
).add_action(
    ClickAction(selector=".next-button")
).add_action(
    LogoutAction(logout_selector=".logout-btn")
)

# Run the bot
success = bot.run()

# Access scraped data and metrics
if success:
    items = bot.context.get('items', [])
    print(f"\nScraped items: {items}")
    print(f"\nBot Metrics:")
    print(json.dumps(bot.metrics.to_dict(), indent=2))