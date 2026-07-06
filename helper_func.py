import base64
import re
import asyncio
import logging
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified
from pyrogram.types import Message, InlineKeyboardMarkup
import pyromod.listen

from config import START_PIC
from database.database import is_admin, is_owner, get_fsub_status, get_fsubs

logger = logging.getLogger(__name__)

async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def safe_edit(message: Message, text: str, buttons=None):
    try:
        if message.photo or message.video or message.document:
            if message.caption != text: await message.edit_caption(caption=text, reply_markup=buttons)
        else:
            if message.text != text: await message.edit_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
    except MessageNotModified: pass
    except Exception:
        try: await message.reply_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
        except: pass

async def get_input(client, message, prompt, keyboard=None):
    new_text = f"{prompt}\n\nSend /cancel to stop."
    await safe_edit(message, new_text)
    
    try:
        msg = await client.listen(message.chat.id, timeout=300)
        if not msg.text or msg.text.lower() == "/cancel":
            return None
        return msg.text
    except asyncio.TimeoutError:
        return None

async def subscribed(client: Client, message: Message) -> bool:
    if not message.from_user: return True
    user_id = message.from_user.id
    if await is_admin(user_id) or await is_owner(user_id): return True
    
    if not await get_fsub_status(): return True 
    
    channels = await get_fsubs()
    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
        except UserNotParticipant: return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
            except: return False
        except Exception: continue
    return True

async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("=")
    return base64.urlsafe_b64decode((base64_string + "=" * (-len(base64_string) % 4)).encode()).decode()

async def get_messages(client, message_ids):
    messages = []
    total = 0
    while total != len(message_ids):
        batch = message_ids[total:total + 200]
        try: msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except: msgs = []
        messages.extend(msgs)
        total += len(batch)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat and message.forward_from_chat.id == client.db_channel.id:
        return message.forward_from_message_id
    if message.text:
        match = re.search(r"https://t.me/(?:c/)?([^/]+)/(\d+)", message.text)
        if match and (match.group(1) == str(client.db_channel.id).replace("-100", "") or match.group(1) == client.db_channel.username):
            return int(match.group(2))
    return 0

def get_readable_time(seconds: int) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    result = []
    if days: result.append(f"{days}d")
    if hours: result.append(f"{hours}h")
    if minutes: result.append(f"{minutes}m")
    if seconds or not result: result.append(f"{seconds}s")
    return " ".join(result)
    
