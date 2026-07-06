import asyncio
import urllib.parse
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import CHANNEL_ID, USER_REPLY_TEXT
from helper_func import encode
from database.database import is_premium

IGNORE_CMDS = ['start','users','broadcast','batch','genlink','stats','settings','maintenance']

@Client.on_message(filters.private & filters.incoming & ~filters.command(IGNORE_CMDS))
async def private_message_handler(client: Client, message: Message):
    if await is_premium(message.from_user.id):
        reply = await message.reply_text("Please Wait...!", quote=True)
        try: post = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
        except: return await reply.edit_text("❌ Failed to forward to DB.")

        link = f"https://t.me/{client.username}?start={await encode(f'get-{post.id * abs(client.db_channel.id)}')}"
        await reply.edit_text(f"<b>Here is your link:</b>\n\n{link}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]]), disable_web_page_preview=True)
    else:
        try: await message.reply_text(USER_REPLY_TEXT, quote=True)
        except: pass

@Client.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    link = f"https://t.me/{client.username}?start={await encode(f'get-{message.id * abs(client.db_channel.id)}')}"
    try: await message.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]]))
    except: pass
        
