# Telegram Aggregator

This project is a Telegram bot that aggregates messages from multiple source channels, summarizes them using OpenAI's GPT model, and forwards the summary to a target channel. It's designed to help users consolidate information from various sources into a single channel for easier consumption.

## Features

- Monitors multiple source Telegram channels
- Summarizes messages using OpenAI's GPT model
- Forwards summarized messages to a specified target channel
- Supports text messages, photos, videos, and documents
- Configurable using environment variables
- Timezone-aware message handling

## Prerequisites

- Python 3.7+
- A Telegram Bot Token
- API ID and API Hash from Telegram
- OpenAI API key

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/oztamir/telegram-aggregator.git
   cd telegram-aggregator
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and fill in your credentials:

   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your specific details:
   - `TELEGRAM_API_ID`: Your Telegram API ID
   - `TELEGRAM_API_HASH`: Your Telegram API Hash
   - `TELEGRAM_PHONE_NUMBER`: Your phone number
   - `TELEGRAM_CHANNELS`: Comma-separated list of source channel usernames or IDs
   - `TARGET_CHANNEL`: The username or ID of the channel where summaries will be sent
   - `OPENAI_API_KEY`: Your OpenAI API key
