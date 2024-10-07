from telethon import TelegramClient as TelethonClient, events, errors
from telethon.tl.types import InputPeerChannel
from telethon.sessions import StringSession
from datetime import datetime, timedelta
import os
import pytz
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables
load_dotenv()


class TelegramClient:
    def __init__(self):
        self.API_ID = os.getenv("TELEGRAM_API_ID")
        self.API_HASH = os.getenv("TELEGRAM_API_HASH")
        self.PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")
        self.CHANNELS = os.getenv("TELEGRAM_CHANNELS").split(",")
        self.TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
        self.MINUTES_AGO = int(
            os.getenv("MINUTES_AGO", "60")
        )  # Default to 60 minutes if not set
        self.client = None

        # Set up logging
        logging.basicConfig(
            format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
            level=logging.INFO,  # Changed from WARNING to INFO
        )
        self.logger = logging.getLogger(__name__)

    async def initialize(
        self, save_session=False, session_string=None, session_file=None
    ):
        self.logger.info("Initializing TelegramClient")
        if session_file:
            with open(session_file, "r") as f:
                session_string = f.read().strip()

        if session_string or save_session:
            session = StringSession(session_string)
        else:
            session = "session"

        self.client = TelethonClient(
            session, self.API_ID, self.API_HASH, flood_sleep_threshold=5
        )
        await self.client.start()

        if not await self.client.is_user_authorized():
            if session_string:
                self.logger.warning("Provided session is not valid or expired.")
                return
            self.logger.info("User not authorized. Sending code request.")
            await self.client.send_code_request(self.PHONE_NUMBER)
            await self.client.sign_in(self.PHONE_NUMBER, input("Enter the code: "))

        self.logger.info("TelegramClient initialized successfully")

    async def save_session(self):
        self.logger.info("Saving session to session.txt")
        with open("session.txt", "w") as f:
            f.write(self.client.session.save())
        self.logger.info("Session saved successfully")
        print("Session saved to session.txt")

    async def fetch_recent_messages(self):
        self.logger.info(f"Fetching messages from the last {self.MINUTES_AGO} minutes")
        minutes_ago = datetime.now(pytz.UTC) - timedelta(minutes=self.MINUTES_AGO)
        all_messages = []

        for channel in self.CHANNELS:
            self.logger.info(f"Fetching messages from channel: {channel}")
            entity = await self.client.get_entity(channel)
            messages = await self.client.get_messages(entity, limit=10)

            if messages:
                for message in reversed(messages):
                    if message.date >= minutes_ago:
                        all_messages.append(
                            self.format_message(message, entity, channel)
                        )

        self.logger.info(f"Fetched {len(all_messages)} messages in total")
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
        self.logger.info(f"Sending summary to target channel: {self.TARGET_CHANNEL}")
        target_entity = await self.client.get_entity(self.TARGET_CHANNEL)
        try:
            highlights_message = await self.client.send_message(
                target_entity, highlights
            )
            await self.client.send_message(
                target_entity, details, comment_to=highlights_message
            )
            self.logger.info("Summary sent successfully")
        except errors.FloodWaitError as e:
            self.logger.error(
                f"FloodWaitError encountered. Required wait time: {e.seconds} seconds."
            )
        except Exception as e:
            self.logger.error(f"An error occurred while sending the summary: {str(e)}")

    async def disconnect(self):
        self.logger.info("Disconnecting TelegramClient")
        await self.client.disconnect()
        self.logger.info("TelegramClient disconnected successfully")
