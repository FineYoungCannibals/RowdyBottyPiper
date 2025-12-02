# YAML Configuration Guide for RowdyBottyPiper

## Overview

RowdyBottyPiper now supports YAML-based bot configuration, making it easier to define workflows without writing Python code. This is especially useful for:

- Quick prototyping
- Non-developers defining workflows
- LLM-assisted bot generation
- Version-controlled workflow definitions
- Easier workflow sharing and documentation

## Basic Structure

```yaml
bot:
  # Bot configuration
  name: "my-bot"
  headless: false
  debug: true

variables:
  # Reusable variables with environment substitution
  base_url: "https://example.com"
  username: "${LOGIN_USER}"

actions:
  # Sequential list of actions
  - type: action_type
    param1: value1
    param2: value2
```

## Bot Configuration

The `bot` section configures the Bot instance:

```yaml
bot:
  name: "my-bot"                    # Required: Bot name
  headless: false                   # Optional: Run in headless mode (default: false)
  debug: false                      # Optional: Enable debug logging (default: false)
  chrome_driver_path: "/path/to/driver"  # Optional: Custom ChromeDriver path
  correlation_id: "${WORKFLOW_ID}"  # Optional: For distributed tracing
```

## Variables Section

Define reusable variables and environment variable substitution:

```yaml
variables:
  base_url: "https://example.com"
  api_endpoint: "${base_url}/api"
  username: "${LOGIN_USERNAME}"     # From environment variable
  password: "${LOGIN_PASSWORD}"
  download_dir: "./downloads/${DATE}"
```

**Environment Variable Syntax**: Use `${VAR_NAME}` to reference environment variables.

**Resolution Order**:
1. Variables defined in `variables` section
2. Environment variables
3. Empty string if not found

## Actions

Actions are executed sequentially. Each action must have a `type` field.

### Common Parameters

All actions support these optional parameters (inherited from Action base class):

```yaml
- type: any_action
  retry_count: 3        # Number of retries on failure (default: 3)
  retry_delay: 2        # Seconds between retries (default: 2)
  wait_lower: 1.1       # Lower bound for random waits (default: 1.1)
  wait_upper: 10.0      # Upper bound for random waits (default: 10.0)
```

### Login Action

Authenticate on a website:

```yaml
- type: login
  url: "https://example.com/login"           # Required: Login page URL
  username: "user@example.com"               # Required: Username/email
  password: "password123"                    # Required: Password
  username_selector: "#email"                # Required: CSS selector for username field
  password_selector: "#password"             # Required: CSS selector for password field
  submit_selector: "button[type='submit']"   # Required: CSS selector for submit button
  success_indicator: ".dashboard"            # Required: CSS selector that appears after login
  retry_with_refresh: true                   # Optional: Retry with page refresh (default: true)
  verification_timeout: 30                   # Optional: Timeout for success verification (default: 30)
```

**Example**:
```yaml
- type: login
  url: "${base_url}/auth/login"
  username: "${USERNAME}"
  password: "${PASSWORD}"
  username_selector: "input[name='username']"
  password_selector: "input[name='password']"
  submit_selector: "#login-btn"
  success_indicator: ".user-profile"
```

### Navigate Action

Navigate to a URL:

```yaml
- type: navigate
  url: "https://example.com/page"   # Required: URL to navigate to
  wait_time: 2                      # Optional: Seconds to wait after navigation
```

**Example**:
```yaml
- type: navigate
  url: "${base_url}/products"
  wait_time: 3
```

### Click Action

Click an element:

```yaml
- type: click
  selector: ".button-class"         # Required: Element selector
  by: "CSS_SELECTOR"               # Optional: Selector type (default: CSS_SELECTOR)
  wait_time: 2                     # Optional: Seconds to wait after click
```

**Selector Types**: 
- `CSS_SELECTOR` (default)
- `XPATH`
- `ID`
- `CLASS_NAME`
- `NAME`
- `LINK_TEXT`
- `PARTIAL_LINK_TEXT`

**Example**:
```yaml
- type: click
  selector: "//button[@id='submit']"
  by: "XPATH"
  wait_time: 1
```

### Scrape Action

Extract data from the page:

```yaml
- type: scrape
  selector: ".product-name"         # Required: CSS selector for elements
  context_key: "product_names"      # Required: Key to store data in context
  attribute: null                   # Optional: Extract attribute instead of text (default: null)
```

**Examples**:

```yaml
# Scrape text content
- type: scrape
  selector: ".product-title"
  context_key: "titles"

# Scrape attribute value
- type: scrape
  selector: ".product"
  context_key: "product_ids"
  attribute: "data-product-id"
```

### Download Action

Download a file:

```yaml
- type: download
  selector: ".download-btn"              # Required: CSS selector for download trigger
  by: "CSS_SELECTOR"                    # Optional: Selector type (default: CSS_SELECTOR)
  download_dir: "./downloads"           # Optional: Download directory (default: ~/Downloads)
  expected_filename: "*.pdf"            # Optional: Expected filename pattern (supports wildcards)
  timeout: 60                           # Optional: Download timeout in seconds (default: 60)
  scroll_to_element: true               # Optional: Scroll to button before clicking (default: true)
  verify_download: true                 # Optional: Verify download completed (default: true)
```

**Example**:
```yaml
- type: download
  selector: "#download-report"
  download_dir: "./reports/${REPORT_DATE}"
  expected_filename: "monthly_report_*.xlsx"
  timeout: 120
```

**Context Data**: Stores download info in context under `last_download`:
```python
{
    'filename': 'report.pdf',
    'filepath': '/path/to/report.pdf',
    'size_bytes': 1024000,
    'download_dir': './downloads'
}
```

### Download Multiple Action

Download multiple files sequentially:

```yaml
- type: download_multiple
  selectors:                            # Required: List of selectors for downloads
    - ".report-1"
    - ".report-2"
    - ".report-3"
  by: "CSS_SELECTOR"                   # Optional: Selector type (default: CSS_SELECTOR)
  download_dir: "./downloads"          # Optional: Download directory
  timeout: 60                          # Optional: Timeout per download (default: 60)
  pause_between_downloads: [2.0, 5.0]  # Optional: Random pause range between downloads
```

**Example**:
```yaml
- type: download_multiple
  selectors:
    - ".download[data-type='sales']"
    - ".download[data-type='inventory']"
    - ".download[data-type='finance']"
  download_dir: "./monthly_reports"
  timeout: 180
  pause_between_downloads: [3.0, 7.0]
```

**Context Data**: Stores all downloads in context under `downloads` (list) and `download_count` (int).

## Slack Notifications (Optional)

Configure automatic Slack notifications:

```yaml
slack:
  notify_on_success: true              # Send notification on success
  notify_on_failure: true              # Send notification on failure
  success_message: "Bot completed!"    # Custom success message
  failure_message: "Bot failed!"       # Custom failure message
```

**Requirements**:
- `RRP_SLACK_BOT_TOKEN` environment variable must be set
- `RRP_SLACK_CHANNEL` environment variable must be set

**Example**:
```yaml
slack:
  notify_on_success: true
  notify_on_failure: true
  success_message: "Monthly report download completed - ${download_count} files"
  failure_message: "Report download failed - check logs for correlation_id: ${bot.correlation_id}"
```

## Complete Example

```yaml
# Complete workflow example
bot:
  name: "ecommerce-scraper"
  headless: true
  debug: false

variables:
  site_url: "https://shop.example.com"
  login_user: "${SHOP_USERNAME}"
  login_pass: "${SHOP_PASSWORD}"
  output_dir: "./data/${DATE}"

actions:
  # Login
  - type: login
    url: "${site_url}/login"
    username: "${login_user}"
    password: "${login_pass}"
    username_selector: "#email"
    password_selector: "#password"
    submit_selector: "button[type='submit']"
    success_indicator: ".account-menu"

  # Navigate to products
  - type: navigate
    url: "${site_url}/products/laptops"
    wait_time: 2

  # Scrape product names
  - type: scrape
    selector: ".product-name"
    context_key: "names"

  # Scrape prices
  - type: scrape
    selector: ".product-price"
    context_key: "prices"
    attribute: "data-price"

  # Click first product
  - type: click
    selector: ".product:first-child"
    wait_time: 2

  # Download spec sheet
  - type: download
    selector: ".download-specs"
    download_dir: "${output_dir}"
    expected_filename: "*_specifications.pdf"
    timeout: 90

  # Navigate to reports
  - type: navigate
    url: "${site_url}/account/reports"

  # Download all monthly reports
  - type: download_multiple
    selectors:
      - ".report[data-month='january']"
      - ".report[data-month='february']"
      - ".report[data-month='march']"
    download_dir: "${output_dir}/reports"
    pause_between_downloads: [2.0, 4.0]

slack:
  notify_on_success: true
  notify_on_failure: true
  success_message: "Scraping completed - check ${output_dir}"
  failure_message: "Scraping failed - check logs"
```

## Usage in Python

### Simple Usage

```python
from rowdybottypiper.loaders.yaml_loader import load_bot_from_yaml

# Load and run
bot = load_bot_from_yaml("config.yaml")
success = bot.run()

# Access context data
if success:
    products = bot.context.get('names', [])
    print(f"Found {len(products)} products")
```

### Advanced Usage

```python
from rowdybottypiper.loaders.yaml_loader import YAMLBotLoader

# Load configuration
loader = YAMLBotLoader(config_path="config.yaml")
bot = loader.create_bot()
slack_config = loader.get_slack_config()

# Run bot
success = bot.run()

# Handle Slack notifications
if slack_config and bot.slack:
    if success and slack_config.get('notify_on_success'):
        bot.notify_slack(
            title="Success",
            message=slack_config.get('success_message')
        )
```

## Tips and Best Practices

1. **Use Variables**: Define common values once and reuse them
2. **Environment Variables**: Keep secrets in environment, not in YAML files
3. **Descriptive Names**: Use clear, descriptive names for context keys
4. **Start Simple**: Begin with a basic workflow and add complexity gradually
5. **Test Incrementally**: Test each action before adding the next
6. **Version Control**: Keep YAML configs in git for change tracking
7. **Documentation**: Add comments to explain complex workflows
8. **Error Handling**: Use appropriate retry counts and timeouts
9. **Validation**: Validate selectors work before running full workflow
10. **Logging**: Enable debug mode during development

## LLM-Assisted Workflow Creation

You can ask an LLM to generate YAML configurations:

**Example Prompt**:
```
Create a RowdyBottyPiper YAML config that:
1. Logs into https://portal.example.com with credentials from environment
2. Navigates to the reports section
3. Scrapes all report titles into context key 'report_titles'
4. Downloads the first 3 reports to ./downloads
5. Sends a Slack notification on completion
```

The LLM will generate a ready-to-use YAML file based on the schema above.

## Troubleshooting

### Config Not Loading
- Check YAML syntax is valid (use a YAML validator)
- Ensure file path is correct
- Check file permissions

### Environment Variables Not Substituting
- Ensure variables are exported: `export VAR_NAME=value`
- Check variable name matches exactly (case-sensitive)
- Use `${VAR_NAME}` syntax, not `$VAR_NAME`

### Action Failing
- Enable debug mode: `debug: true`
- Check selectors are correct (test in browser DevTools)
- Increase timeouts if needed
- Add wait_time after navigation

### Download Not Working
- Ensure download directory exists or is creatable
- Check download_dir path is correct
- Increase timeout for large files
- Verify expected_filename pattern matches

## Future Enhancements

Planned features for future versions:

- **Conditionals**: If/then/else logic based on context
- **Loops**: Iterate over scraped data
- **Custom Actions**: Load user-defined action classes
- **Dry Run Mode**: Validate config without execution
- **Action Groups**: Reusable action sequences
- **Schema Validation**: Validate YAML against schema
- **Visual Editor**: GUI for creating YAML configs