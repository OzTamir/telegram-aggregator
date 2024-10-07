from telethon import TelegramClient, events
from telethon.tl.types import InputPeerChannel
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
import openai
import pytz  # Add this import at the top of your file

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")

# List of channel usernames to aggregate
CHANNELS = os.getenv("TELEGRAM_CHANNELS").split(",")

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ... rest of the code ...


async def main():
    async with TelegramClient("session", API_ID, API_HASH) as client:
        # Ensure we're authorized
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            await client.sign_in(PHONE_NUMBER, input("Enter the code: "))

        # Make one_hour_ago timezone-aware (UTC)
        one_hour_ago = datetime.now(pytz.UTC) - timedelta(hours=1)
        all_messages = []

        for channel in CHANNELS:
            entity = await client.get_entity(channel)
            messages = await client.get_messages(entity, limit=50)

            if messages:
                for message in reversed(messages):
                    if message.date >= one_hour_ago:
                        message_time = message.date.strftime("%H:%M")
                        message_text = message.text if message.text else "[Media]"
                        message_link = f"https://t.me/{channel}/{message.id}"
                        all_messages.append(
                            {
                                "channel": entity.title,
                                "time": message_time,
                                "text": message_text,
                                "link": message_link,
                            }
                        )

        if all_messages:
            summary = create_summary(all_messages)
            print(summary)
        else:
            print("No messages found in the last hour.")


def create_summary(messages):
    # Prepare the messages for the API request
    messages_text = "\n".join(
        [f"{m['channel']} [{m['time']}]: {m['text']} ({m['link']})" for m in messages]
    )

    system_prompt = """
    You are a helpful assistant that summarizes Telegram messages from news channels.
    The user will send a list of messages from different channels, and your job is to summarize the news events they describe into a single message.
    Your response should be a list of news events, where each event is a bullet point.
    Each bullet point should be a concise summary of the news event, and under it a list of links to the messages that reported the event.
    For each link, add a short description of the message as it was described by the channel.

    Note that different channels may report the same event at different times (or talk about the same event but from a different perspective),
    and you should understand that it's the same event and group the reports into a single bullet point.

    Example:
    ```
    * Terrorist attack in Jerusalem - three people were killed and several others injured.
        - [ChannelName] [HH:MM]: Terrorist attack in Jerusalem - three people were killed and several others injured. [Link to message]
        - [ChannelName] [HH:MM]: Another terrorist attack in Jerusalem - two people were killed and several others injured. [Link to message]
        - [ChannelName] [HH:MM]: Terrorist attack in Jerusalem - three people were killed and several others injured. [Link to message]
    ```

    Everything you write should be in the same language as the messages (Hebrew).
    """

    user_prompt = f"Summarize the following Telegram messages:\n\n{messages_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].message["content"].strip()


if __name__ == "__main__":
    asyncio.run(main())
