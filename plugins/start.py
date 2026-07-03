import asyncio
import logging
import humanize
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import (
    is_user_present, add_user, is_user_banned, 
    get_ban_reason, is_maintenance, is_admin, user_data
)

logging.basicConfig(level=logging.INFO)
AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    first_name = message.from_user.first_name or "User"
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""

    if not await subscribed(client, message):
        buttons = []
        if client.invitelink: buttons.append(InlineKeyboardButton("Join Channel 1", url=client.invitelink))
        if client.invitelink2: buttons.append(InlineKeyboardButton("Join Channel 2", url=client.invitelink2))
        row2 = []
        if client.invitelink3: row2.append(InlineKeyboardButton("Join Channel 3", url=client.invitelink3))
        if client.invitelink4: row2.append(InlineKeyboardButton("Join Channel 4", url=client.invitelink4))
            
        keyboard = [buttons, row2] if row2 else [buttons]
        return await message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name, last=last_name, username=username, mention=message.from_user.mention, id=user_id), reply_markup=InlineKeyboardMarkup(keyboard))

    if await is_user_banned(user_id):
        reason = await get_ban_reason(user_id)
        return await message.reply_text(f"🚫 You are banned.\nReason: {reason}")

    if not await is_user_present(user_id):
        try:
            await add_user(user_id, first_name, username)
            await client.send_message(LOG_CHANNEL_ID, f"New User: {message.from_user.mention} ({user_id})")
        except Exception as e: logging.error(e)

    if await is_maintenance(user_id):
        return await message.reply_text("🛠 Maintenance mode ON")

    if len(text.split()) > 1:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
        except: return

        ids = []
        try:
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

        copied_msgs = []
        for msg in messages:
            caption = msg.caption.html if msg.caption else ""
            try:
                copied = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT)
                copied_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT)
                copied_msgs.append(copied)
            except: pass

        warn = await client.send_message(
            chat_id=user_id,
            text=(f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In <b>{file_auto_delete}</b> (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There."),
            parse_mode=ParseMode.HTML
        )
        asyncio.create_task(delete_files(copied_msgs, client, warn, base64_string))
        return

    admin_status = await is_admin(user_id)
    buttons = [[InlineKeyboardButton("🧠 HELP", callback_data="help"), InlineKeyboardButton("🔰 ABOUT", callback_data="about")]]
    if admin_status: buttons.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])

    await message.reply_photo(photo=START_PIC, caption=START_MSG.format(first=first_name, last=last_name, username=username, mention=message.from_user.mention, id=user_id), reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("users") & filters.private)
async def total_users(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("Admins only")
    total = await user_data.count_documents({})
    await message.reply_text(f"Total Users: {total}")

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("❌ You are not authorized to use this command.")
    if not message.reply_to_message:
        msg = await message.reply_text("❌ Reply to a message to broadcast.")
        await asyncio.sleep(8)
        try:
            await msg.delete()
            await message.delete()
        except: pass
        return

    pls_wait = await message.reply_text("📢 Broadcasting... Please wait...")
    total = await user_data.count_documents({})
    successful, blocked, deleted, unsuccessful = 0, 0, 0, 0

    async for user in user_data.find({}, {"_id": 1}):
        try:
            await message.reply_to_message.copy(user["_id"])
            successful += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user["_id"])
                successful += 1
            except: unsuccessful += 1
        except Exception as e:
            error = str(e).lower()
            if "blocked" in error: blocked += 1
            elif "deactivated" in error or "deleted" in error: deleted += 1
            else: unsuccessful += 1

    status = f"<b>📢 Broadcast Completed</b>\n<b>Total Users:</b> <code>{total}</code>\n<b>Successful:</b> <code>{successful}</code>\n<b>Blocked Users:</b> <code>{blocked}</code>\n<b>Deleted Accounts:</b> <code>{deleted}</code>\n<b>Unsuccessful:</b> <code>{unsuccessful}</code>"
    await pls_wait.edit_text(status, parse_mode=ParseMode.HTML)
    await asyncio.sleep(15)
    try:
        await pls_wait.delete()
        await message.delete()
    except: pass

async def delete_files(messages, client, main_message, payload=None):
    if not AUTO_DELETE_ENABLED: return
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except: pass

    keyboard = None
    if payload: keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Get File Again", url=f"https://t.me/{client.username}?start={payload}")]])
    try: await main_message.edit_text(text="✅ <b>Your Video / File Has Been Deleted.</b>\n\n👇 Click the button below to get your file again.", parse_mode=ParseMode.HTML, reply_markup=keyboard)
    except: pass

def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state

def get_auto_delete() -> bool:
    global AUTO_DELETE_ENABLED
    return AUTO_DELETE_ENABLED

@Client.on_message(filters.command("autodeleteon") & filters.private)
async def enable_autodelete(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("❌ Admins only.")
    set_auto_delete(True)
    await message.reply_text("✅ Auto delete ON")

@Client.on_message(filters.command("autodeleteoff") & filters.private)
async def disable_autodelete(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("❌ Admins only.")
    set_auto_delete(False)
    await message.reply_text("✅ Auto delete OFF")
    
