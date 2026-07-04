import asyncio
import urllib.parse
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON, USER_REPLY_TEXT
from helper_func import encode
from database.Database import is_premium

IGNORE_CMDS = [
    'start','users','broadcast','batch','genlink','stats','joinchannels','pypi',
    'restart','settings','joinchannelon','joinchanneloff','admin','autodelete',
    'autodeleteon','autodeleteoff','maintenance','ban','unban','bannedlist',
    'addadmin','removeadmin','adminlist', 'about', 'help'
]

@Client.on_message(filters.private & filters.incoming & ~filters.command(IGNORE_CMDS))
async def private_message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    if await is_premium(user_id):
        reply_text = await message.reply_text("Please Wait...!", quote=True)
        try:
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
        except Exception as e:
            return await reply_text.edit_text(f"Something went wrong: {e}")

        converted_id = post_message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        share_url = urllib.parse.quote(link)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={share_url}")]])
        await reply_text.edit_text(f"<b>Here is your link</b>\n\n{link}", reply_markup=keyboard, disable_web_page_preview=True)

        if not DISABLE_CHANNEL_BUTTON:
            try: await post_message.edit_reply_markup(keyboard)
            except: pass
    else:
        try: await message.reply_text(USER_REPLY_TEXT, quote=True)
        except: pass

@Client.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON: return
    
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={share_url}")]])
    try: await message.edit_reply_markup(keyboard)
    except: pass
        
