import sys
import asyncio
from datetime import datetime, timezone, timedelta
from aiohttp import web
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import pyrogram.utils
from pyrogram.errors import UserIsBlocked, UserDeactivated

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT
from database.database import premium_collection, remove_premium
from plugins.route import routes

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"} if False else None, 
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.logger = LOGGER(__name__)
        self.app = web.Application(client_max_size=30000000)
        self.app.add_routes(routes)

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
                        try: await self.send_message(user_id, f"⚠️ <b>Your premium membership has ended.</b>")
                        except: pass
                    elif warning_time > expires_at and not user.get("notified", False):
                        try:
                            await self.send_message(user_id, f"⚠️ <b>Reminder:</b> Your premium membership is closing soon!")
                            await premium_collection.update_one({"_id": user_id}, {"$set": {"notified": True}})
                        except: pass
            except Exception as e:
                self.logger.error(f"Premium check error: {e}")
            await asyncio.sleep(3600)

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now(timezone.utc)
        self.username = me.username
        
        asyncio.create_task(self.premium_expiry_task())
        
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            msg = await self.send_message(db_channel.id, "Bot Started")
            await msg.delete()
        except Exception as e:
            self.logger.error(f"❌ CRITICAL: Bot is not admin in DB channel {CHANNEL_ID}. Error: {e}")
            sys.exit()

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        self.logger.info(f"✅ Web Server started successfully on port {PORT}")

        self.set_parse_mode(ParseMode.HTML)
        self.logger.info(f"Bot Running: @{self.username}")

    async def stop(self, *args):
        await super().stop()
        self.logger.info("Bot stopped cleanly.")
        
