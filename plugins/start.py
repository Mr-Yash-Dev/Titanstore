import asyncio
import logging
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import FORCE_PIC, FORCE_MSG, LOG_CHANNEL_ID, START_PIC, START_MSG
from helper_func import subscribed, decode, get_messages
from database.database import (
    is_user_present, add_user, is_user_banned, get_ban_reason, 
    is_maintenance, is_admin, get_settings, get_fsub_channels
)

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    if await is_user_banned(user_id):
        return await message.reply_text(f"🚫 Banned.\nReason: {await get_ban_reason(user_id)}")

    if await is_maintenance(user_id):
        return await message.reply_text("🛠 Maintenance mode ON")

    if not await subscribed(client, message):
        channels = await get_fsub_channels()
        buttons = []
        for index, ch in enumerate(channels, start=1):
            link = client.invitelinks.get(ch)
            if link: buttons.append([InlineKeyboardButton(f"Join Channel {index}", url=link)])
        
        return await message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))

    if not await is_user_present(user_id):
        await add_user(user_id, first_name, username)
        try: await client.send_message(LOG_CHANNEL_ID, f"#New_User\nID: <code>{user_id}</code>\nName: {message.from_user.mention}")
        except: pass

    if len(text.split()) > 1:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
            ids = []
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1)
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
        except: return

        temp = await message.reply_text("⏳ Processing...")
        messages = await get_messages(client, ids)
        await temp.delete()

        settings = await get_settings()
        is_protected = settings.get("protect_content", False)
        auto_del = settings.get("auto_delete", True)
        timer = settings.get("auto_delete_timer", 60)
        
        copied_msgs = []
        for msg in messages:
            if msg.empty: continue 
            caption = msg.caption.html if msg.caption else ""
            try:
                copied = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, protect_content=is_protected)
                copied_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, protect_content=is_protected)
                copied_msgs.append(copied)
            except: pass

        if not copied_msgs: return await message.reply_text("❌ Files unavailable.")

        if auto_del:
            warn = await client.send_message(user_id, f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nDeleted in <b>{humanize.naturaldelta(timer)}</b>.")
            asyncio.create_task(delete_files(copied_msgs, client, warn, base64_string, timer))
        return

    admin_status = await is_admin(user_id)
    buttons = [[InlineKeyboardButton("🧠 HELP", callback_data="help"), InlineKeyboardButton("🔰 ABOUT", callback_data="about")]]
    if admin_status: buttons.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])

    await message.reply_photo(photo=START_PIC, caption=START_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))

async def delete_files(messages, client, main_message, payload, timer):
    await asyncio.sleep(timer)
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except: pass

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Get File Again", url=f"https://t.me/{client.username}?start={payload}")]])
    try: await main_message.edit_text("✅ <b>Deleted.</b>\n👇 Click below to get again.", reply_markup=keyboard)
    except: pass
        
