import urllib.parse
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, get_message_id
from database.database import is_premium

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    if not await is_premium(message.from_user.id): return

    while True:
        try: first_message = await client.ask(chat_id=message.from_user.id, text="Forward FIRST message", filters=(filters.forwarded | filters.text), timeout=60)
        except asyncio.TimeoutError: return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id: break
        await first_message.reply_text("❌ Invalid message")

    while True:
        try: second_message = await client.ask(chat_id=message.from_user.id, text="Forward LAST message", filters=(filters.forwarded | filters.text), timeout=60)
        except asyncio.TimeoutError: return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id: break
        await second_message.reply_text("❌ Invalid message")

    if f_msg_id > s_msg_id: f_msg_id, s_msg_id = s_msg_id, f_msg_id
    base64_string = await encode(f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]])
    await second_message.reply_text(f"<b>Batch link:</b>\n{link}", reply_markup=keyboard)

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if not await is_premium(message.from_user.id): return
    while True:
        try: channel_message = await client.ask(chat_id=message.from_user.id, text="Forward message", filters=(filters.forwarded | filters.text), timeout=60)
        except asyncio.TimeoutError: return
        msg_id = await get_message_id(client, channel_message)
        if msg_id: break
        await channel_message.reply_text("❌ Invalid message")

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share", url=f"https://telegram.me/share/url?url={urllib.parse.quote(link)}")]])
    await channel_message.reply_text(f"<b>Link:</b>\n{link}", reply_markup=keyboard)
    
