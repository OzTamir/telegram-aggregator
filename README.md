# Telegram Aggregator

This project is a Telegram bot that aggregates messages from multiple source channels and forwards them to a target channel. It's designed to help users consolidate information from various sources into a single channel for easier consumption.

## Features

- Monitors multiple source Telegram channels
- Forwards messages to a specified target channel
- Supports text messages, photos, videos, and documents
- Configurable using environment variables

## Prerequisites

- Python 3.7+
- A Telegram Bot Token
- API ID and API Hash from Telegram

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/telegram-aggregator.git
   cd telegram-aggregator
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and fill in your Telegram API credentials:

   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your specific details:
   - `API_ID`: Your Telegram API ID
   - `API_HASH`: Your Telegram API Hash
   - `BOT_TOKEN`: Your Telegram Bot Token
   - `SOURCE_CHANNELS`: Comma-separated list of source channel usernames or IDs
   - `TARGET_CHANNEL`: Username or ID of the target channel

## Usage

Run the bot using the following command:
