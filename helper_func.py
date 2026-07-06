import base64
import re
import asyncio
import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified
from config import START_PIC
from database.database import is_admin, get_settings, get_fsub_channels

logger = logging.getLogger(__name__)

async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def safe_edit(message, text, buttons=None):
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
    try:
        if message.photo or message.video or message.document: await message.edit_caption(caption=new_text)
        else:
            if message.text != new_text: await message.edit_text(new_text)
    except MessageNotModified: pass
    except Exception: pass

    try:
        msg = await client.listen(message.chat.id, timeout=300)
        if not msg.text:
            m = await message.reply("❌ Invalid input!")
            asyncio.create_task(auto_delete(m))
            return None
        if msg.text.lower() == "/cancel":
            m = await message.reply("❌ Cancelled!")
            asyncio.create_task(auto_delete(m))
            return None
        return msg.text
    except asyncio.TimeoutError:
        m = await message.reply("⌛ Timeout!")
        asyncio.create_task(auto_delete(m))
        return None

async def subscribed(client, message) -> bool:
    if not message.from_user: return True
    user_id = message.from_user.id
    if await is_admin(user_id): return True

    settings = await get_settings()
    if not settings.get("fsub_mode", False): return True

    channels = await get_fsub_channels()
    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                return False
        except UserNotParticipant: return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
            except: return False
        except Exception as e:
            logger.error(f"Force Sub Error ({channel}): {e}")
            continue
    return True

async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()

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
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id: return message.forward_from_message_id
        return 0
    if message.forward_sender_name: return 0
    if message.text:
        pattern = r"https://t.me/(?:c/)?([^/]+)/(\d+)"
        match = re.search(pattern, message.text)
        if not match: return 0
        chat, msg_id = match.group(1), int(match.group(2))
        if f"-100{chat}" == str(client.db_channel.id) or chat == str(client.db_channel.id): return msg_id
        elif client.db_channel.username and chat == client.db_channel.username: return msg_id
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
    
