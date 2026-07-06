from datetime import datetime, timezone
from pyrogram import filters, Client
from pyrogram.types import Message

from config import BOT_STATS_TEXT
from helper_func import get_readable_time
from database.database import is_admin

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("⚠️ Access Denied: Admins only!")

    now = datetime.now(timezone.utc)
    delta = now - client.uptime
    uptime = get_readable_time(int(delta.total_seconds()))

    await message.reply(BOT_STATS_TEXT.format(uptime=uptime))
    
