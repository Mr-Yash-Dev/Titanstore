from datetime import datetime, timezone
from pyrogram import filters, Client
from pyrogram.types import Message
from config import BOT_STATS_TEXT, ADMINS
from helper_func import get_readable_time
from database.database import (
    is_admin, user_data, admins_collection, banned_users, premium_collection, 
    fsub_collection, get_fsub_status, get_auto_delete, get_protect_status
)

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    m = await message.reply("⏳ Fetching database metrics...")

    now = datetime.now(timezone.utc)
    uptime = get_readable_time(int((now - client.uptime).total_seconds()))

    tot_users = await user_data.count_documents({})
    tot_admins = (await admins_collection.count_documents({})) + len(ADMINS) + 1
    tot_banned = await banned_users.count_documents({"is_banned": True})
    tot_premium = await premium_collection.count_documents({"is_premium": True})
    tot_fsub = await fsub_collection.count_documents({})
    
    fsub_stat = "ON ✅" if await get_fsub_status() else "OFF ❌"
    timer = await get_auto_delete()
    ad_stat = f"ON ✅ ({timer}s)" if timer > 0 else "OFF ❌"
    pc_stat = "ON ✅" if await get_protect_status() else "OFF ❌"

    await m.edit_text(BOT_STATS_TEXT.format(
        uptime=uptime, tot_users=tot_users, tot_admins=tot_admins, 
        tot_banned=tot_banned, tot_premium=tot_premium, 
        fsub_stat=fsub_stat, tot_fsub=tot_fsub, ad_stat=ad_stat, pc_stat=pc_stat
    ))
    
