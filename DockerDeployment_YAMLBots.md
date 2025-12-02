# Docker Deployment Guide for YAML-Configured Bots

## Overview

With YAML configuration support, deploying bots in Docker is now incredibly simple. Each bot runs in its own container with a mounted YAML config file.

## Quick Start

### 1. Build the Docker Image

```bash
# From your rowdybottypiper project root
docker build -t rowdybottypiper:latest .
```

### 2. Create Your Bot Config

```bash
mkdir -p configs
```

Create `configs/my_bot.yaml`:

```yaml
bot:
  name: "my-docker-bot"
  headless: true

variables:
  site_url: "https://example.com"
  username: "${LOGIN_USERNAME}"
  password: "${LOGIN_PASSWORD}"

actions:
  - type: login
    url: "${site_url}/login"
    username: "${username}"
    password: "${password}"
    username_selector: "#email"
    password_selector: "#password"
    submit_selector: "button"
    success_indicator: ".dashboard"

  - type: scrape
    selector: ".data-item"
    context_key: "items"

slack:
  notify_on_success: true
  success_message: "Bot completed successfully!"
```

### 3. Create Environment File

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
LOGIN_USERNAME=your_username
LOGIN_PASSWORD=your_password
SLACK_TOKEN=xoxb-your-token
SLACK_CHANNEL=C1234567890
```

### 4. Run with Docker Compose

```bash
docker-compose up product-scraper
```

## Configuration Path Priority

The bot will look for config in this order:

1. **`RRP_CONFIG_PATH` environment variable** (most specific)
   ```yaml
   environment:
     - RRP_CONFIG_PATH=/custom/path/config.yaml
   ```

2. **`/etc/rowdybottypiper/config.yaml`** (Docker/production default)
   ```yaml
   volumes:
     - ./configs/my_bot.yaml:/etc/rowdybottypiper/config.yaml:ro
   ```

3. **`./config.yaml`** (local development fallback)

## Deployment Patterns

### Pattern 1: Single Bot (Simplest)

**Directory Structure:**
```
my-bot/
├── docker-compose.yml
├── .env
└── config.yaml
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  bot:
    image: rowdybottypiper:latest
    volumes:
      - ./config.yaml:/etc/rowdybottypiper/config.yaml:ro
      - ./downloads:/app/downloads
    env_file: .env
    restart: unless-stopped
    command: python -c "from rowdybottypiper import load_bot_from_yaml; load_bot_from_yaml().run()"
```

**Run:**
```bash
docker-compose up -d
```

### Pattern 2: Multiple Bots

**Directory Structure:**
```
bots/
├── docker-compose.yml
├── .env
└── configs/
    ├── bot1.yaml
    ├── bot2.yaml
    └── bot3.yaml
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  bot1:
    image: rowdybottypiper:latest
    volumes:
      - ./configs/bot1.yaml:/etc/rowdybottypiper/config.yaml:ro
    env_file: .env
    environment:
      - RRP_SLACK_CHANNEL=C111111  # Override per bot
    restart: unless-stopped

  bot2:
    image: rowdybottypiper:latest
    volumes:
      - ./configs/bot2.yaml:/etc/rowdybottypiper/config.yaml:ro
    env_file: .env
    environment:
      - RRP_SLACK_CHANNEL=C222222
    restart: unless-stopped
```

### Pattern 3: Scheduled Execution

**With External Scheduler (Recommended):**

Use a cron job or Kubernetes CronJob to run containers:

```bash
# crontab entry
0 2 * * * docker-compose -f /path/to/docker-compose.yml up bot
```

**With Internal Loop:**

```yaml
services:
  daily-bot:
    image: rowdybottypiper:latest
    volumes:
      - ./config.yaml:/etc/rowdybottypiper/config.yaml:ro
    env_file: .env
    command: |
      sh -c '
        while true; do
          echo "Running at $(date)"
          python -c "from rowdybottypiper import load_bot_from_yaml; load_bot_from_yaml().run()"
          sleep 86400  # 24 hours
        done
      '
```

### Pattern 4: With Custom Script

For complex workflows, use a custom Python script:

**run_bot.py:**
```python
#!/usr/bin/env python3
from rowdybottypiper import load_bot_from_yaml
import sys

def main():
    try:
        # Load bot from default location
        bot = load_bot_from_yaml()
        
        # Run bot
        success = bot.run()
        
        # Custom post-processing
        if success:
            items = bot.context.get('items', [])
            print(f"Scraped {len(items)} items")
            
            # Send custom Slack notification
            if bot.slack:
                bot.notify_slack(
                    title="Custom Report",
                    message=f"Found {len(items)} items"
                )
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)

if __name__ == '__main__':
    main()
```

**docker-compose.yml:**
```yaml
services:
  custom-bot:
    image: rowdybottypiper:latest
    volumes:
      - ./config.yaml:/etc/rowdybottypiper/config.yaml:ro
      - ./run_bot.py:/app/run.py:ro
    env_file: .env
    command: python /app/run.py
```

## Volume Mounts

### Essential Mounts

```yaml
volumes:
  # Config (read-only)
  - ./config.yaml:/etc/rowdybottypiper/config.yaml:ro
  
  # Downloads directory (read-write)
  - ./downloads:/app/downloads
  
  # Data directory (read-write)
  - ./data:/app/data
  
  # Logs (optional, read-write)
  - ./logs:/var/log/bots
```

### Example with All Mounts

```yaml
services:
  full-bot:
    image: rowdybottypiper:latest
    volumes:
      # Config
      - ./configs/bot.yaml:/etc/rowdybottypiper/config.yaml:ro
      
      # Data directories
      - ./downloads:/app/downloads
      - ./reports:/app/reports
      - ./data:/app/data
      
      # Logs
      - ./logs:/var/log/bots
      
      # Custom scripts (optional)
      - ./scripts:/app/scripts:ro
    environment:
      - RRP_CONFIG_PATH=/etc/rowdybottypiper/config.yaml
    env_file: .env
```

## Environment Variables

### Required Variables

Set in `.env` or docker-compose.yml:

```bash
# For actions using credentials
LOGIN_USERNAME=user@example.com
LOGIN_PASSWORD=secret123

# For Slack notifications (optional)
RRP_SLACK_BOT_TOKEN=xoxb-...
RRP_SLACK_CHANNEL=C1234567890
```

### Optional Variables

```bash
# Custom config path
RRP_CONFIG_PATH=/custom/path/config.yaml

# Correlation ID for distributed tracing
CORRELATION_ID=workflow-123

# Timezone
TZ=America/New_York

# Custom variables used in your YAML
REPORT_DATE=2024-01
BASE_URL=https://example.com
```

## Building for Production

### Multi-stage Build (Smaller Image)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget gnupg unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .

RUN mkdir -p /etc/rowdybottypiper /app/downloads /app/data
ENV RRP_CONFIG_PATH=/etc/rowdybottypiper/config.yaml

CMD ["python", "-c", "from rowdybottypiper import load_bot_from_yaml; load_bot_from_yaml().run()"]
```

### Build and Tag

```bash
# Build
docker build -t rowdybottypiper:1.4.0 .
docker tag rowdybottypiper:1.4.0 rowdybottypiper:latest

# Push to registry (optional)
docker tag rowdybottypiper:1.4.0 myregistry/rowdybottypiper:1.4.0
docker push myregistry/rowdybottypiper:1.4.0
```

## Monitoring and Logs

### View Logs

```bash
# Follow logs
docker-compose logs -f bot-name

# Last 100 lines
docker-compose logs --tail=100 bot-name

# All bots
docker-compose logs -f
```

### JSON Logs

Configure structured logging in your Python:

```python
from rowdybottypiper.logging.config import setup_logging

setup_logging(
    log_level="INFO",
    json_format=True,  # JSON for log aggregation
    log_to_file=True,
    log_file_path="/var/log/bots/bot.log"
)
```

Mount logs directory:
```yaml
volumes:
  - ./logs:/var/log/bots
```

### Health Checks

Add health checks to docker-compose.yml:

```yaml
services:
  bot:
    image: rowdybottypiper:latest
    healthcheck:
      test: ["CMD", "python", "-c", "import rowdybottypiper; print('ok')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Troubleshooting

### Bot Can't Find Config

**Error:** `FileNotFoundError: Config file not found`

**Solutions:**
1. Check mount path:
   ```bash
   docker-compose exec bot ls -la /etc/rowdybottypiper/
   ```

2. Verify environment variable:
   ```bash
   docker-compose exec bot env | grep RRP_CONFIG
   ```

3. Check file permissions:
   ```bash
   ls -la configs/your_config.yaml
   ```

### Environment Variables Not Working

**Error:** Config has empty values where variables should be

**Solutions:**
1. Check .env file exists:
   ```bash
   ls -la .env
   ```

2. Verify variables are set:
   ```bash
   docker-compose config
   ```

3. Export before running:
   ```bash
   export LOGIN_USERNAME=user@example.com
   docker-compose up
   ```

### Chrome Issues in Container

**Error:** `chrome not reachable` or `chrome crashed`

**Solutions:**
1. Ensure headless mode:
   ```yaml
   bot:
     headless: true  # Required in Docker
   ```

2. Add Chrome flags in bot config if needed (advanced)

3. Increase shared memory:
   ```yaml
   services:
     bot:
       shm_size: '2gb'  # Or use /dev/shm mount
   ```

## Best Practices

1. **Use headless mode** - Required in Docker
   ```yaml
   bot:
     headless: true
   ```

2. **Read-only config** - Prevent accidental modification
   ```yaml
   volumes:
     - ./config.yaml:/etc/rowdybottypiper/config.yaml:ro
   ```

3. **Secrets in environment** - Never in YAML files
   ```yaml
   variables:
     password: "${PASSWORD}"  # From environment
   ```

4. **Persistent data** - Mount volumes for downloads
   ```yaml
   volumes:
     - ./downloads:/app/downloads
   ```

5. **Structured logging** - Use JSON format for log aggregation

6. **Health checks** - Monitor bot status

7. **Restart policies** - `unless-stopped` or `on-failure`

8. **Resource limits** - Prevent runaway containers
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 2G
   ```

## Example Complete Setup

**Project structure:**
```
my-bots/
├── docker-compose.yml
├── Dockerfile
├── .env
├── configs/
│   ├── scraper1.yaml
│   └── scraper2.yaml
├── downloads/
├── data/
└── logs/
```

**Deploy:**
```bash
# Build
docker build -t rowdybottypiper:latest .

# Run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Success! 🎉

Your bots are now running in Docker with YAML configuration! Each bot is:
- ✅ Isolated in its own container
- ✅ Configured via mounted YAML
- ✅ Using environment variables for secrets
- ✅ Persisting data via volumes
- ✅ Logging to mounted directories
- ✅ Sending Slack notifications

Deploy, scale, and manage your bots with ease!