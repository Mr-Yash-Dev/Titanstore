from datetime import datetime, timezone
from pyrogram import filters, Client
from pyrogram.types import Message

from config import BOT_STATS_TEXT
from helper_func import get_readable_time

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client: Client, message: Message):
    now = datetime.now(timezone.utc)
    delta = now - client.uptime
    uptime = get_readable_time(int(delta.total_seconds()))

    await message.reply(BOT_STATS_TEXT.format(uptime=uptime))
    
