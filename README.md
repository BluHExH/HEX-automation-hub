# HEX Automation Hub

A production-ready, multi-purpose automation tool supporting web scraping, API automation, browser automation, RPA workflows, and social media bots.
![My image](https://github.com/BluHExH/BluHExH/blob/main/IMG_20251105_073905.png)
## Features

- **Web Scraping / Crawling**: Static and JS-heavy site scraping with concurrent fetching
- **API Automation / ETL**: Configurable endpoints with async requests and data processing
- **Browser Automation / UI Tasks**: Headless browser interactions with screenshot capabilities
- **RPA / Workflow Automation**: Local OS tasks, file operations, and Excel/CSV processing
- **Social Media / Messaging Bot Automation**: Telegram, Discord, and Twitter bots
- **Configurable via JSON**: Flexible configuration for all automation types
- **CLI Interface**: Command-line interface with multiple options
- **Docker Support**: Containerized deployment with docker-compose
- **Comprehensive Logging**: Structured logs with rotating file handlers
- **Extensible Architecture**: Plugin system for custom extractors and actions

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Chromium/Chrome browser (for browser automation)

### Quick Installation

```bash
# Clone the repository
git clone <repository-url>
cd HEX-automation-hub

# Install dependencies
make install
# or
./run.sh install
```

### Termux Installation

```bash
# On Termux
./run.sh install
```

### Docker Installation

```bash
# Build and run with Docker
make docker-build
# or
docker build -t hex-automation-hub .

# Run with docker-compose
make deploy
# or
docker-compose up -d
```

## Configuration

Create a `config.json` file based on the `config_example.json`:

```bash
cp config_example.json config.json
```

### Configuration Structure

```json
{
  "web_scraper": {
    "mode": "static|js",
    "base_url": "https://example.com",
    "selectors": {
      "title": "h1",
      "content": ".content"
    },
    "pagination": {
      "param": "page",
      "start": 1,
      "end": 10
    }
  },
  "api": {
    "endpoints": [
      {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {},
        "params": {}
      }
    ],
    "concurrency": 5,
    "retry": 3
  },
  "browser": {
    "headless": true,
    "remote_url": "",
    "tasks": [
      {
        "type": "click",
        "selector": "#submit"
      }
    ]
  },
  "rpa": {
    "tasks": [
      "file_copy",
      "email_send",
      "excel_update"
    ],
    "schedule": "0 * * * *"
  },
  "social_bots": {
    "telegram": {
      "token": "YOUR_TELEGRAM_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    },
    "discord": {},
    "twitter": {
      "consumer_key": "YOUR_CONSUMER_KEY",
      "consumer_secret": "YOUR_CONSUMER_SECRET",
      "access_token": "YOUR_ACCESS_TOKEN",
      "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    }
  },
  "storage": {
    "type": "csv|json|sqlite",
    "path": "data/output.db",
    "unique_key": "id"
  },
  "notifications": {
    "telegram": true,
    "slack": false,
    "email": false
  },
  "logging": {
    "level": "DEBUG",
    "file": "logs/app.log"
  }
}
```

## Usage

### CLI Commands

```bash
# Run a specific automation target
python cli.py run --target web_scraper --config config.json

# Run once and exit
python cli.py run --target api --config config.json --once

# Run in daemon mode (loop)
python cli.py run --target social_bots --config config.json --daemon

# Test a target in dry-run mode
python cli.py test-target --target browser --config config.json

# Export results
python cli.py export --format csv --config config.json
```

### Using the Runner Script

```bash
# Run with the runner script (works on Termux and Linux)
./run.sh run --target web_scraper --config config.json --once
```

### Using Docker

```bash
# Run with Docker
docker run --rm -v $(pwd)/config.json:/app/config.json hex-automation-hub run --target web_scraper --once

# Run with docker-compose
docker-compose run --rm hex-automation-hub run --target api --once
```

## Automation Modules

### 1. Web Scraping / Crawling

Supports both static and JavaScript-heavy websites:

- Static scraping using requests + BeautifulSoup
- JS-heavy scraping using Selenium
- Async concurrent fetching with aiohttp
- Pagination, selector configuration, retry/backoff, rate-limiting, proxy support
- Output formats: CSV, JSON Lines, SQLite
- Telegram notifications for summary/errors
- Dry-run mode and debug logs

### 2. API Automation / ETL

- Configurable endpoints: GET/POST/PUT/DELETE
- Async API requests with httpx/aiohttp
- Retry + backoff + rate-limit
- Response processing + storage (DB / CSV / JSON)
- Scheduled run: cron / Celery / GitHub Actions
- Webhook / Slack / Telegram notifications

### 3. Browser Automation / UI Tasks

- Headless Chrome / Chromium (Selenium or Playwright)
- UI interactions (click, fill, extract)
- Screenshot on error
- Remote WebDriver support for Termux fallback
- Logging & retry mechanism

### 4. RPA / Workflow Automation

- Local OS tasks: file operations, email, Excel / CSV processing
- Task scheduling & chaining (sequence of actions)
- Conditional triggers (if/else based on file/content)
- Cross-platform: Linux, Termux (with fallback)

### 5. Social Media / Messaging Bot Automation

- Telegram / Discord / Twitter/X bots
- Auto post, message, fetch, or monitor
- OAuth / token management
- Configurable triggers and message templates
- Async, retry, logging, storage support

## Testing

### Run All Tests

```bash
make test
# or
python -m pytest tests/ -v
```

### Run Specific Tests

```bash
# Run unit tests
make test-unit

# Run specific module tests
make test-web-scraper
make test-api
make test-browser
make test-rpa
make test-social
```

## Deployment

### Using Deploy Script

```bash
# Deploy the application
./deploy.sh deploy

# Stop the application
./deploy.sh stop

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Extensibility

The HEX Automation Hub is designed with extensibility in mind:

1. **Plugin Architecture**: JSON/YAML "extractors" / action descriptors
2. **Custom Transformations**: Add custom functions for regex, parsing, normalization
3. **Easy Integration**: Simple to add new targets, tasks, or bots

To extend functionality:

1. Create new modules in the `automation/` directory
2. Add corresponding tests in the `tests/` directory
3. Update the CLI interface in `cli.py` to support new targets
4. Update the configuration schema as needed

## Troubleshooting

### Common Issues

1. **Browser Automation Not Working**:
   - Ensure Chromium/Chrome is installed
   - Check if the correct WebDriver is installed
   - Verify the `remote_url` configuration for remote WebDriver

2. **API Requests Failing**:
   - Check network connectivity
   - Verify API endpoints and authentication
   - Increase timeout values in configuration

3. **Permission Errors**:
   - Ensure proper file permissions for data and log directories
   - Run with appropriate user privileges

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs in the `logs/` directory
2. Run with `--debug` flag for detailed output
3. File an issue on the project repository

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Notice

Please use this tool responsibly and in compliance with all applicable laws and website terms of service. See [LEGAL.md](LEGAL.md) for more information.
