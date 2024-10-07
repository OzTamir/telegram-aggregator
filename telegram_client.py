from telethon import TelegramClient as TelethonClient, events
from telethon.tl.types import InputPeerChannel
from telethon.sessions import StringSession
from datetime import datetime, timedelta
import os
import pytz


class TelegramClient:
    def __init__(self):
        self.API_ID = os.getenv("TELEGRAM_API_ID")
        self.API_HASH = os.getenv("TELEGRAM_API_HASH")
        self.PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")
        self.CHANNELS = os.getenv("TELEGRAM_CHANNELS").split(",")
        self.TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
        self.client = None

    async def initialize(
        self, save_session=False, session_string=None, session_file=None
    ):
        if session_file:
            with open(session_file, "r") as f:
                session_string = f.read().strip()

        if session_string or save_session:
            session = StringSession(session_string)
        else:
            session = "session"

        self.client = TelethonClient(session, self.API_ID, self.API_HASH)
        await self.client.start()

        if not await self.client.is_user_authorized():
            if session_string:
                print("Provided session is not valid or expired.")
                return
            await self.client.send_code_request(self.PHONE_NUMBER)
            await self.client.sign_in(self.PHONE_NUMBER, input("Enter the code: "))

    async def save_session(self):
        with open("session.txt", "w") as f:
            f.write(self.client.session.save())
        print("Session saved to session.txt")

    async def fetch_recent_messages(self):
        one_hour_ago = datetime.now(pytz.UTC) - timedelta(hours=1)
        all_messages = []

        for channel in self.CHANNELS:
            entity = await self.client.get_entity(channel)
            messages = await self.client.get_messages(entity, limit=50)

            if messages:
                for message in reversed(messages):
                    if message.date >= one_hour_ago:
                        all_messages.append(
                            self.format_message(message, entity, channel)
                        )

        return all_messages

    def format_message(self, message, entity, channel):
        israel_tz = pytz.timezone("Asia/Jerusalem")
        message_time = message.date.astimezone(israel_tz).strftime("%H:%M")
        message_text = message.text if message.text else "[Media]"
        message_link = f"https://t.me/{channel}/{message.id}"
        return {
            "channel": entity.title,
            "time": message_time,
            "text": message_text,
            "link": message_link,
        }

    def split_summary(self, summary):
        highlights, details = summary.split("[END OF SUMMARY]")
        return highlights.strip(), details.strip()

    async def send_summary(self, highlights, details):
        target_entity = await self.client.get_entity(self.TARGET_CHANNEL)
        highlights_message = await self.client.send_message(target_entity, highlights)
        await self.client.send_message(
            target_entity, details, comment_to=highlights_message
        )
