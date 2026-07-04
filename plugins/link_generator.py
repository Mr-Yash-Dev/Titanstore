import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout

from helper_func import encode, get_message_id
from database.database import is_premium

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_premium(user_id): return

    while True:
        try:
            first_message = await client.ask(chat_id=user_id, text="Forward FIRST message from DB channel\nor send DB post link", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id: break
        await first_message.reply_text("❌ Invalid message (not from DB channel)")

    while True:
        try:
            second_message = await client.ask(chat_id=user_id, text="Forward LAST message from DB channel\nor send DB post link", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id: break
        await second_message.reply_text("❌ Invalid message (not from DB channel)")

    if f_msg_id > s_msg_id:
        f_msg_id, s_msg_id = s_msg_id, f_msg_id

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={share_url}")]])
    await second_message.reply_text(f"<b>Here is your batch link:</b>\n\n{link}", reply_markup=keyboard)

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_premium(user_id): return

    while True:
        try:
            channel_message = await client.ask(chat_id=user_id, text="Forward message from DB channel\nor send DB post link", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        msg_id = await get_message_id(client, channel_message)
        if msg_id: break
        await channel_message.reply_text("❌ Invalid message (not from DB channel)")

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={share_url}")]])
    await channel_message.reply_text(f"<b>Here is your link:</b>\n\n{link}", reply_markup=keyboard)
    
