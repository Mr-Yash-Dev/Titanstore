from datetime import datetime, timezone
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from helper_func import get_readable_time
from database.database import (
    is_admin, get_total_users, get_total_banned, get_total_admins, 
    get_total_premium, get_settings, get_fsub_channels
)

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⚠️ You do not have permission to view stats.")

    msg = await message.reply("📊 Fetching metrics...")
    
    # Calculate Uptime
    now = datetime.now(timezone.utc)
    delta = now - client.uptime
    uptime = get_readable_time(int(delta.total_seconds()))

    # Fetch Data
    total_users = await get_total_users()
    total_banned = await get_total_banned()
    total_admins = await get_total_admins()
    total_premium = await get_total_premium()
    
    settings = await get_settings()
    fsub_channels = await get_fsub_channels()
    
    fsub_mode = "ON ✅" if settings.get("fsub_mode") else "OFF ❌"
    protect_mode = "ON ✅" if settings.get("protect_content") else "OFF ❌"
    auto_del_mode = "ON ✅" if settings.get("auto_delete") else "OFF ❌"
    auto_del_timer = settings.get("auto_delete_timer", 60)

    stats_text = f"""
<b>🤖 SYSTEM METRICS</b>
• <b>Uptime:</b> <code>{uptime}</code>

<b>👥 USER METRICS</b>
• <b>Total Users:</b> <code>{total_users}</code>
• <b>Total Admins:</b> <code>{total_admins}</code>
• <b>Premium Users:</b> <code>{total_premium}</code>
• <b>Banned Users:</b> <code>{total_banned}</code>

<b>⚙️ BOT CONFIGURATIONS</b>
• <b>F-Sub Mode:</b> {fsub_mode}
• <b>Total F-Sub Channels:</b> <code>{len(fsub_channels)}</code>
• <b>Auto-Delete Mode:</b> {auto_del_mode} (<i>{auto_del_timer}s</i>)
• <b>Protect Content:</b> {protect_mode}
"""

    await msg.edit_text(stats_text, parse_mode=ParseMode.HTML)
    
