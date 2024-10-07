import asyncio
import argparse
import os
from telegram_client import TelegramClient
from openai_summarizer import create_summary


async def main(save_session=False, session_string=None, session_file=None):
    # If no session string or file is provided, check the environment variable
    if not session_string and not session_file:
        session_string = os.getenv("TELEGRAM_SESSION_STRING")

    telegram_client = TelegramClient()
    await telegram_client.initialize(save_session, session_string, session_file)

    if save_session:
        await telegram_client.save_session()
        return

    messages = await telegram_client.fetch_recent_messages()

    if messages:
        summary = create_summary(messages)
        print(summary)

        highlights, details = telegram_client.split_summary(summary)
        await telegram_client.send_summary(highlights, details)
    else:
        print("No messages found in the last hour.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram message aggregator")
    parser.add_argument(
        "--save-session", action="store_true", help="Save the session to a file"
    )
    parser.add_argument(
        "--session", type=str, help="Session string to use for authentication"
    )
    parser.add_argument(
        "--session-file", type=str, help="File containing the session string"
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            save_session=args.save_session,
            session_string=args.session,
            session_file=args.session_file,
        )
    )
