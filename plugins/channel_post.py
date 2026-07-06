import asyncio
import urllib.parse
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import CHANNEL_ID, USER_REPLY_TEXT
from helper_func import encode
from database.database import is_premium

IGNORE_CMDS = ['start','users','broadcast','batch','genlink','stats','maintenance']

@Client.on_message(filters.private & filters.incoming & ~filters.command(IGNORE_CMDS))
async def private_message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if await is_premium(user_id):
        reply_text = await message.reply_text("Please Wait...!", quote=True)
        try: post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
        except Exception as e: return await reply_text.edit_text(f"Error: {e}")

        base64_string = await encode(f"get-{post_message.id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]])
        
        await reply_text.edit_text(f"<b>Link:</b>\n{link}", reply_markup=keyboard)
    else:
        try: await message.reply_text(USER_REPLY_TEXT, quote=True)
        except: pass

@Client.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    base64_string = await encode(f"get-{message.id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]])
    try: await message.edit_reply_markup(keyboard)
    except: pass
        
