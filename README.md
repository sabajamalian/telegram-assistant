# Telegram Echo Bot

A simple Telegram bot that echoes back messages and logs detailed message metadata.

## Setup Instructions

1. **Create a Telegram Bot**
   - Open Telegram and search for "@BotFather"
   - Start a chat with BotFather and send `/newbot`
   - Follow the instructions to create your bot
   - BotFather will give you a token - copy it

2. **Configure environment variables**
   - Create a `.env` file in the project root
   - Add your Telegram bot token:
     ```
     TELEGRAM_TOKEN=your_telegram_bot_token_here
     ```

## Running the Bot

### Option 1: Local Run

1. **Create and activate a virtual environment**

   On Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python bot.py
   ```

### Option 2: Docker Run

1. **Build the Docker image**
   ```bash
   docker build -t telegram-bot .
   ```

2. **Run the bot**
   ```bash
   docker run --env-file .env telegram-bot
   ```

   Or if you want to run it in the background:
   ```bash
   docker run -d --env-file .env telegram-bot
   ```

## Using the Bot

1. Open Telegram and search for your bot using the username you created
2. Start a chat with your bot
3. Send `/start` to get the welcome message
4. Send any text message, and the bot will echo it back

## Features

- Responds to `/start` command with a welcome message
- Echoes back any text message
- Logs detailed message metadata including:
  - Message ID and timestamp
  - Chat information
  - User information
  - Message content and type
- Secure token storage using environment variables
- Docker support for easy deployment 