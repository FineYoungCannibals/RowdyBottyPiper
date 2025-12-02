# Docker Deployment - Quick Reference

## 🐳 New Docker-Friendly Features

The YAML loader now has **Docker-first defaults**!

### Config Path Priority (Automatic)

1. **`RBP_CONFIG_PATH` env var** → Use custom path
2. **`/etc/rowdybottypiper/config.yaml`** → Docker standard location
3. **`./config.yaml`** → Local development fallback

**No path needed!** Just mount your config and run:

```python
from rowdybottypiper import load_bot_from_yaml
bot = load_bot_from_yaml()  # Automatically finds config!
bot.run()
```

## 📦 Quick Start

### 1. Create Your Config

`configs/my_bot.yaml`:
```yaml
bot:
  name: "docker-bot"
  headless: true

variables:
  username: "${LOGIN_USERNAME}"
  password: "${LOGIN_PASSWORD}"

actions:
  - type: login
    url: "https://example.com/login"
    username: "${username}"
    password: "${password}"
    username_selector: "#email"
    password_selector: "#password"
    submit_selector: "button"
    success_indicator: ".dashboard"
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'
services:
  bot:
    image: rowdybottypiper:latest
    volumes:
      # Mount config to Docker default location
      - ./configs/my_bot.yaml:/etc/rowdybottypiper/config.yaml:ro
      - ./downloads:/app/downloads
    environment:
      - LOGIN_USERNAME=user@example.com
      - LOGIN_PASSWORD=secret123
      - RBP_SLACK_BOT_TOKEN=${SLACK_TOKEN}
      - RBP_SLACK_CHANNEL=${SLACK_CHANNEL}
    restart: unless-stopped
```

### 3. Run

```bash
docker-compose up -d
```

**That's it!** The bot will:
- ✅ Auto-find config at `/etc/rowdybottypiper/config.yaml`
- ✅ Use environment variables from docker-compose
- ✅ Send Slack notifications if configured
- ✅ Save downloads to mounted volume

## 🎯 Three Deployment Patterns

### Pattern 1: Standard Location (Recommended)

```yaml
volumes:
  - ./my_bot.yaml:/etc/rowdybottypiper/config.yaml:ro
# No RBP_CONFIG_PATH needed - auto-detected!
```

### Pattern 2: Custom Location

```yaml
volumes:
  - ./my_bot.yaml:/app/custom.yaml:ro
environment:
  - RBP_CONFIG_PATH=/app/custom.yaml
```

### Pattern 3: Multiple Bots

```yaml
services:
  bot1:
    volumes:
      - ./bot1.yaml:/etc/rowdybottypiper/config.yaml:ro
  
  bot2:
    volumes:
      - ./bot2.yaml:/etc/rowdybottypiper/config.yaml:ro
```

Each bot auto-finds its own config!

## 📁 Files Included

### Core Docker Files
- **`docker-compose.yml`** - Multiple bot examples
- **`Dockerfile`** - Production-ready image
- **`.env.example`** - Environment variables template
- **`DOCKER_DEPLOYMENT_GUIDE.md`** - Complete guide

### Updated Core
- **`yaml_loader.py`** - Now with Docker-friendly defaults!

## 🚀 Deployment Commands

```bash
# Build image
docker build -t rowdybottypiper:latest .

# Single bot
docker-compose up -d bot-name

# All bots
docker-compose up -d

# View logs
docker-compose logs -f bot-name

# Stop
docker-compose down
```

## 🎨 Example Project Structure

```
my-bots/
├── docker-compose.yml       # Multi-bot orchestration
├── Dockerfile              # Image definition
├── .env                    # Secrets (don't commit!)
├── configs/
│   ├── scraper1.yaml      # Bot 1 config
│   ├── scraper2.yaml      # Bot 2 config
│   └── reporter.yaml      # Bot 3 config
├── downloads/             # Shared downloads
├── data/                  # Shared data
└── logs/                  # Shared logs
```

## ⚙️ Environment Variables

Create `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

Example `.env`:
```bash
# Credentials
LOGIN_USERNAME=user@example.com
LOGIN_PASSWORD=secret123

# Slack
RBP_SLACK_BOT_TOKEN=xoxb-your-token
RBP_SLACK_CHANNEL=C1234567890

# Custom variables
REPORT_DATE=2024-01
BASE_URL=https://example.com
```

## 🔒 Security Best Practices

1. **Never commit `.env`** - Add to `.gitignore`
2. **Use read-only mounts** - `:ro` on config files
3. **Secrets in environment** - Not in YAML
4. **Limit resources** - Prevent runaway containers
5. **Update regularly** - Keep Chrome/ChromeDriver current

## 📊 Monitoring

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# Follow logs
docker-compose logs -f bot-name

# Last 100 lines
docker-compose logs --tail=100 bot-name
```

### Restart Bot
```bash
docker-compose restart bot-name
```

## 🐛 Troubleshooting

### Can't Find Config
```bash
# Check mount
docker-compose exec bot ls -la /etc/rowdybottypiper/

# Check env vars
docker-compose exec bot env | grep RRP
```

### Environment Variables Empty
```bash
# Verify .env exists
ls -la .env

# Check docker-compose config
docker-compose config
```

### Chrome Issues
Ensure `headless: true` in bot config:
```yaml
bot:
  headless: true  # Required in Docker!
```

## 🎉 Benefits

### For You (Ops)
- ✅ One image, many bots
- ✅ Simple config mounting
- ✅ Easy scaling
- ✅ Clear separation of concerns
- ✅ Version control friendly

### For Your Bots
- ✅ Auto-config discovery
- ✅ Environment-based secrets
- ✅ Consistent logging
- ✅ Isolated execution
- ✅ Easy debugging

## 📚 Full Documentation

- **Complete Guide**: `DOCKER_DEPLOYMENT_GUIDE.md`
- **YAML Reference**: `YAML_CONFIG_GUIDE.md`
- **Integration Steps**: `INTEGRATION_GUIDE.md`
- **Examples**: `docker-compose.yml`

## ✅ Ready to Deploy!

You now have everything needed for Docker deployment:
- ✅ Auto-config discovery
- ✅ Environment variable support
- ✅ Multiple deployment patterns
- ✅ Production-ready Dockerfile
- ✅ Complete examples
- ✅ Comprehensive documentation

**Deploy your bots with confidence!** 🚀