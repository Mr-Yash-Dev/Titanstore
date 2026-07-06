import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import (
    FORCE_PIC, FORCE_MSG, LOG_CHANNEL_ID, START_PIC, 
    START_MSG, PROTECT_CONTENT, FILE_AUTO_DELETE
)
from helper_func import subscribed, decode, get_messages, get_readable_time
from database.database import (
    is_user_present, add_user, is_user_banned, get_ban_reason, 
    is_maintenance, is_admin, get_auto_delete_status
)

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    # Check Force Sub
    if not await subscribed(client, message):
        buttons = []
        # Fetching pre-generated links from bot.py cache for blazing fast response
        for i, key in enumerate(["fs1", "fs2", "fs3", "fs4"], start=1):
            link = client.invitelinks.get(key)
            if link:
                buttons.append([InlineKeyboardButton(f"Join Channel {i}", url=link)])
        
        return await message.reply_photo(
            photo=FORCE_PIC, 
            caption=FORCE_MSG.format(first=first_name), 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Check Ban Status
    if await is_user_banned(user_id):
        return await message.reply_text(f"🚫 You are banned.\nReason: {await get_ban_reason(user_id)}")

    # Add New User
    if not await is_user_present(user_id):
        await add_user(user_id, first_name, username)
        try: 
            await client.send_message(LOG_CHANNEL_ID, f"#New_User\nID: <code>{user_id}</code>\nName: {first_name}")
        except: 
            pass

    # Check Maintenance Status
    if await is_maintenance(user_id):
        return await message.reply_text("🛠 Maintenance mode ON. Normal operations are temporarily paused.")

    # Process File Link (Payload)
    if len(text.split()) > 1:
        try:
            argument = (await decode(text.split(" ", 1)[1])).split("-")
            if len(argument) == 3:
                ids = range(int(argument[1]) // abs(client.db_channel.id), (int(argument[2]) // abs(client.db_channel.id)) + 1)
            else:
                ids = [int(argument[1]) // abs(client.db_channel.id)]
        except Exception:
            return

        temp = await message.reply_text("⏳ Processing...")
        messages = await get_messages(client, ids)
        await temp.delete()

        copied_msgs = []
        
        for msg in messages:
            if msg.empty: continue 
            try:
                copied = await msg.copy(
                    chat_id=user_id, 
                    caption=msg.caption.html if msg.caption else "", 
                    parse_mode=ParseMode.HTML, 
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(
                    chat_id=user_id, 
                    caption=msg.caption.html if msg.caption else "", 
                    parse_mode=ParseMode.HTML, 
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)
            except Exception as e:
                logging.error(f"Copy error: {e}")

        if not copied_msgs: 
            return await message.reply("❌ **Error:** Files unavailable or deleted from the database.")

        # Auto Delete Logic
        is_auto_delete_on = await get_auto_delete_status()
        if is_auto_delete_on and FILE_AUTO_DELETE > 0:
            warn = await message.reply(f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis File Will Be Deleted In <b>{get_readable_time(FILE_AUTO_DELETE)}</b>.")
            asyncio.create_task(delete_files(copied_msgs, client, warn, text.split(" ", 1)[1], FILE_AUTO_DELETE))
        return

    # Standard Start Menu
    btn = [[InlineKeyboardButton("🧠 HELP", callback_data="help"), InlineKeyboardButton("🔰 ABOUT", callback_data="about")]]
    if await is_admin(user_id): 
        btn.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])
        
    await message.reply_photo(
        photo=START_PIC, 
        caption=START_MSG.format(first=first_name), 
        reply_markup=InlineKeyboardMarkup(btn)
    )

async def delete_files(messages, client, main_message, payload, timer):
    await asyncio.sleep(timer)
    for msg in messages:
        try: 
            await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except Exception: 
            pass
    try: 
        await main_message.edit_text(
            text="✅ <b>Your File Has Been Deleted.</b>\n👇 Click below to get it again.", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Get File Again", url=f"https://t.me/{client.username}?start={payload}")]])
        )
    except Exception: 
        pass
        
