# VPN Bot Setup Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Payment system accounts (YooMoney, QIWI, etc.)
- VPN server with API access

## 🚀 Quick Setup

### 1. Get Your Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow instructions to create your bot
4. Save the bot token

### 2. Clone and Install

```bash
git clone https://github.com/Vlasik2010/TgBot_vpn.git
cd TgBot_vpn
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Required settings:**
```bash
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_telegram_id,another_admin_id
```

**Optional settings:**
```bash
DATABASE_URL=sqlite:///vpn_bot.db
YOOMONEY_TOKEN=your_yoomoney_token
VPN_SERVER_URL=your_vpn_server.com
```

### 4. Test and Run

```bash
# Validate setup
python validate_bot.py

# Run the bot
python bot/main.py
```

## 🔧 Configuration Options

### Bot Settings
- `BOT_TOKEN` - Your Telegram bot token
- `ADMIN_IDS` - Comma-separated admin Telegram IDs
- `DEBUG` - Enable debug mode (True/False)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

### Database Settings
- `DATABASE_URL` - Database connection string
  - SQLite: `sqlite:///vpn_bot.db`
  - PostgreSQL: `postgresql://user:pass@host/db`

### Payment Settings
- `YOOMONEY_TOKEN` - YooMoney API token
- `QIWI_TOKEN` - QIWI API token

### VPN Settings
- `VPN_SERVER_URL` - Your VPN server URL
- `VPN_API_KEY` - VPN server API key

### Pricing (in rubles)
- `PLAN_1_MONTH_PRICE=299`
- `PLAN_3_MONTH_PRICE=799`
- `PLAN_6_MONTH_PRICE=1499`
- `PLAN_12_MONTH_PRICE=2699`

## 💳 Payment Integration

### YooMoney Setup
1. Register at [yoomoney.ru](https://yoomoney.ru)
2. Get API token in developer section
3. Configure webhook URL for payment notifications

### QIWI Setup
1. Register at [qiwi.com](https://qiwi.com)
2. Get API key from merchant account
3. Configure payment notifications

## 🔒 VPN Server Integration

The bot supports various VPN protocols:

### WireGuard (Recommended)
- Fast and modern
- Easy to configure
- Good mobile support

### OpenVPN
- Widely supported
- High security
- More complex setup

### Custom Integration
Modify `bot/utils/helpers.py` to integrate with your VPN provider's API.

## 🛠️ Customization

### Adding New Languages
1. Copy `locales/ru.py` to `locales/your_language.py`
2. Translate all messages
3. Update bot configuration

### Custom Payment Methods
1. Add new payment handler in `bot/utils/helpers.py`
2. Update payment flow in `bot/handlers/main.py`
3. Add new buttons in localization files

### Subscription Plans
Edit `bot/config/settings.py` to modify plans:

```python
SUBSCRIPTION_PLANS = {
    'new_plan': {
        'name': 'New Plan',
        'price': 999,
        'duration_days': 60,
        'description': 'Custom plan description'
    }
}
```

## 📊 Monitoring

### Logs
Bot logs are stored in `logs/bot.log`. Monitor for:
- Payment errors
- User registration issues
- API failures

### Database
Access database with:
```bash
sqlite3 vpn_bot.db
# or use your preferred database tool
```

### Admin Commands
- `/admin` - Access admin panel
- View statistics
- Manage users
- Send broadcasts

## 🔧 Troubleshooting

### Common Issues

**Bot doesn't start:**
- Check bot token validity
- Ensure all dependencies installed
- Verify Python version (3.8+)

**Payments not working:**
- Verify payment provider tokens
- Check webhook configuration
- Monitor payment provider logs

**VPN configs not generated:**
- Check VPN server connectivity
- Verify API credentials
- Test VPN server API manually

### Getting Help

1. Check logs in `logs/bot.log`
2. Run `python validate_bot.py` for diagnostics
3. Verify configuration in `.env` file

## 🚀 Production Deployment

### Using systemd (Linux)

1. Create service file `/etc/systemd/system/vpn-bot.service`:
```ini
[Unit]
Description=VPN Telegram Bot
After=network.target

[Service]
Type=simple
User=vpnbot
WorkingDirectory=/path/to/TgBot_vpn
Environment=PATH=/path/to/TgBot_vpn/venv/bin
ExecStart=/path/to/TgBot_vpn/venv/bin/python bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
systemctl enable vpn-bot
systemctl start vpn-bot
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot/main.py"]
```

### Environment Variables for Production

```bash
# Production settings
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@host/db

# Enable SSL for webhooks
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_PORT=8443
```

## 📈 Scaling

### Database
- Use PostgreSQL for production
- Set up database backups
- Monitor database performance

### Load Balancing
- Use multiple bot instances
- Implement Redis for session storage
- Use reverse proxy (nginx)

### Monitoring
- Set up application monitoring
- Monitor payment success rates
- Track user engagement metrics

---

**Need help?** Create an issue on GitHub or contact support.