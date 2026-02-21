# reminderbot

A Telegram bot that sends trash pickup reminders sourced from the AWB Köln public API. It notifies all registered users at **19:00 Europe/Berlin** the evening before a scheduled pickup.

## Features

- Automatic nightly notifications before every pickup
- Multi-user: flatmates can self-register with `/start`
- On-demand commands to check upcoming pickups
- Owner-only `/test` command to verify end-to-end delivery
- Calendar data cached locally and refreshed daily

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Register to receive notifications |
| `/stop` | Unsubscribe from notifications |
| `/naechste` | Show the next upcoming pickup |
| `/woche` | Show all pickups this week |
| `/hilfe` | Show help |
| `/test` | Send a test notification to all users (owner only) |

## Setup

### 1. Create a Telegram bot

Talk to [@BotFather](https://t.me/BotFather) on Telegram, create a new bot, and copy the token.

### 2. Get your chat ID

Send a message to your bot, then open:
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
Your chat ID is in `result[0].message.chat.id`.

### 3. Configure environment

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional — defaults shown
SCHEDULE_TIME=19:00
TIMEZONE=Europe/Berlin
DATA_DIR=./data

# AWB address parameters (building_number and street_code from AWB Köln)
AWB_BUILDING_NUMBER=your_building_number
AWB_STREET_CODE=your_street_code
```

### 4. Run with Docker

```bash
docker compose up -d --build
```

Data (calendar cache and user list) is persisted in `./data/` via a volume mount.

## Project Structure

```
bot.py            # Entry point, scheduler setup, handler registration
config.py         # Environment variable loading
awb.py            # AWB Köln API client and disk cache
users.py          # Persistent user store (data/users.json)
notifications.py  # Notification logic, fan-out to all users
commands.py       # Telegram command handlers
formatting.py     # German text formatting
```

## Supported Waste Types

| API value | Label |
|-----------|-------|
| `grey` | Restmülltonne |
| `brown` | Biotonne |
| `blue` | Papiertonne |
| `wertstoff` | Wertstofftonne |
| `xmastree` | Weihnachtsbaum |
