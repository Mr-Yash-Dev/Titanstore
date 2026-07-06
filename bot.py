import sys
import asyncio
from datetime import datetime, timedelta, timezone
from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import pyrogram.utils
from pyrogram.errors import FloodWait, UserIsBlocked, UserDeactivated

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT
from database.database import premium_collection, remove_premium, get_fsub_channels

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.logger = LOGGER(__name__)
        self.invitelinks = {}

    async def premium_expiry_task(self):
        while True:
            try:
                now = datetime.now(timezone.utc)
                warning_time = now + timedelta(days=1)
                cursor = premium_collection.find({"is_premium": True})
                async for user in cursor:
                    user_id = user["_id"]
                    expires_at = user.get("expires_at")
                    if not expires_at: continue
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                    if now > expires_at:
                        await remove_premium(user_id)
                        try: await self.send_message(user_id, f"⚠️ <b>Your premium membership ended.</b>")
                        except: pass
                    elif warning_time > expires_at and not user.get("notified", False):
                        try:
                            await self.send_message(user_id, f"⚠️ <b>Reminder:</b> Premium closing soon!")
                            await premium_collection.update_one({"_id": user_id}, {"$set": {"notified": True}})
                        except: pass
            except Exception as e: self.logger.error(f"Premium check error: {e}")
            await asyncio.sleep(3600) 

    async def fetch_fsub_links(self):
        channels = await get_fsub_channels()
        self.invitelinks.clear()
        for channel_id in channels:
            try:
                chat = await self.get_chat(channel_id)
                link = chat.invite_link or await self.export_chat_invite_link(channel_id)
                self.invitelinks[channel_id] = link
            except Exception as e:
                self.logger.error(f"Failed to get link for {channel_id}: {e}")

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now(timezone.utc)
        self.username = me.username
        
        asyncio.create_task(self.premium_expiry_task())
        await self.fetch_fsub_links()

        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            msg = await self.send_message(self.db_channel.id, "Test Message")
            await msg.delete()
        except Exception as e:
            self.logger.error(f"CRITICAL: DB Channel error: {e}")
            sys.exit()

        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            site = web.TCPSite(app, "0.0.0.0", PORT)
            await site.start()
            self.logger.info(f"Web Server started on port {PORT}")
        except Exception as e:
            self.logger.warning(f"Web Server failed: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.logger.info(f"Bot Running - @{self.username}")

    async def stop(self, *args):
        await super().stop()
        
