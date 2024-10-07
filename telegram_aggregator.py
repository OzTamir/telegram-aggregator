from telethon import TelegramClient, events
from telethon.tl.types import InputPeerChannel
from telethon.sessions import StringSession
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
import openai
import pytz  # Add this import at the top of your file
import argparse

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

# Add this line to get the target channel
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")


async def main(save_session=False, session_string=None, session_file=None):
    if session_file:
        with open(session_file, "r") as f:
            session_string = f.read().strip()

    if session_string or save_session:
        session = StringSession(session_string)
    else:
        session = "session"

    async with TelegramClient(session, API_ID, API_HASH) as client:
        if not await client.is_user_authorized():
            if session_string:
                print("Provided session is not valid or expired.")
                return
            await client.send_code_request(PHONE_NUMBER)
            await client.sign_in(PHONE_NUMBER, input("Enter the code: "))

        if save_session:
            # Save the session string to a file
            with open("session.txt", "w") as f:
                f.write(client.session.save())
            print("Session saved to session.txt")
            return

        # Make one_hour_ago timezone-aware (UTC)
        one_hour_ago = datetime.now(pytz.UTC) - timedelta(hours=1)
        all_messages = []

        for channel in CHANNELS:
            entity = await client.get_entity(channel)
            messages = await client.get_messages(entity, limit=50)

            if messages:
                for message in reversed(messages):
                    if message.date >= one_hour_ago:
                        israel_tz = pytz.timezone("Asia/Jerusalem")
                        message_time = message.date.astimezone(israel_tz).strftime(
                            "%H:%M"
                        )
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

            # Split the summary into highlights and details
            highlights, details = summary.split("[END OF SUMMARY]")
            highlights = highlights.strip()
            details = details.strip()

            # Send the highlights to the target channel
            target_entity = await client.get_entity(TARGET_CHANNEL)
            highlights_message = await client.send_message(target_entity, highlights)

            # Reply to the highlights with the details
            await client.send_message(
                target_entity, details, comment_to=highlights_message
            )
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
    Begin your response with a list of the news events, without too many details on each one.
    
    After the list, go into more detail on each event.
    Each bullet point should be a concise summary of the news event, and under it a list of links to the messages that reported the event.
    For each link, add a short description of the message as it was described by the channel.

    Note that different channels may report the same event at different times (or talk about the same event but from a different perspective),
    and you should understand that it's the same event and group the reports into a single bullet point.

    Example (where it says [END OF SUMMARY] keep it as a token - I will use it to split the summary into sections):
    ```
    להלן סיכום האירועים העיקריים:

    • פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    • [Add more bullet points for other main events]

    [END OF SUMMARY]
    ──────────
    *️⃣ פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו

    🔹 [ChannelName] [HH:MM]: פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel1/123456

    🔹 [ChannelName] [HH:MM]: פיגוע טרור נוסף בירושלים - שני אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel2/123456

    🔹 [ChannelName] [HH:MM]: פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel3/123456

    ──────────

    [Add more detailed bullet points for other events]
    ```

    Remember to replace the placeholder text and links with actual summarized content from the messages.
    ```

    Add a seperator between each bullet point.
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
