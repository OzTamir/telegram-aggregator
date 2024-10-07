# Telegram Aggregator

This project is a Telegram bot that aggregates messages from multiple source channels, summarizes them using OpenAI's GPT model, and forwards the summary to a target channel. It's designed to help users consolidate information from various sources into a single channel for easier consumption.

## Features

- Monitors multiple source Telegram channels
- Summarizes messages using OpenAI's GPT model
- Forwards summarized messages to a specified target channel
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

## Usage

To run the Telegram Aggregator, use the following command:

```
python main.py
```

### Command-line Arguments

- `--save-session`: Save the session to a file for future use
- `--session <session_string>`: Use a provided session string for authentication
- `--session-file <file_path>`: Use a session string stored in a file

Example:

```
python main.py --save-session
python main.py --session "your_session_string_here"
python main.py --session-file session.txt
```

## Docker Support

This project includes a Dockerfile for easy deployment. To build and run the Docker container:

1. Build the Docker image:

   ```
   docker build -t telegram-aggregator .
   ```

2. Run the container:
   ```
   docker run --env-file .env telegram-aggregator
   ```

Make sure your `.env` file is properly configured before running the Docker container.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
