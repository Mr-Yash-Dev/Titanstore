import base64
import re
import asyncio
import logging

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified

from config import FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from database.database import is_admin, is_owner

logger = logging.getLogger(__name__)

async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def safe_edit(message, text, buttons=None):
    try:
        # Check if the message has a photo/media. If it does, edit the caption instead of text!
        if message.photo or message.video or message.document:
            if message.caption != text:
                await message.edit_caption(caption=text, reply_markup=buttons)
        else:
            if message.text != text:
                await message.edit_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
    except MessageNotModified:
        pass
    except Exception as e:
        try: await message.reply_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
        except: pass

async def get_input(client, message, prompt):
    new_text = f"{prompt}\n\nSend /cancel to stop."
    try:
        # Keep the photo when asking for input!
        if message.photo or message.video or message.document:
            await message.edit_caption(caption=new_text)
        else:
            if message.text != new_text:
                await message.edit_text(new_text)
    except MessageNotModified: pass
    except Exception: pass

    try:
        msg = await client.listen(message.chat.id, timeout=300)
        if not msg.text:
            m = await msg.reply("❌ Invalid input!")
            asyncio.create_task(auto_delete(m))
            return None
        if msg.text.lower() == "/cancel":
            m = await msg.reply("❌ Cancelled!")
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
    
    if await is_admin(user_id) or await is_owner(user_id): return True

    channels = [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]
    for channel in channels:
        if not channel: continue
        try:
            chat_id = int(channel) if str(channel).startswith("-100") or str(channel).isdigit() else channel
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                return False
        except UserNotParticipant:
            return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                member = await client.get_chat_member(chat_id, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
            except: return False
        except Exception as e:
            logger.error(f"Error checking force sub for channel {channel}: {e}")
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
        try:
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except: msgs = []
        messages.extend(msgs)
        total += len(batch)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0
    if message.forward_sender_name: return 0
    if message.text:
        pattern = r"https://t.me/(?:c/)?([^/]+)/(\d+)"
        match = re.search(pattern, message.text)
        if not match: return 0
        chat, msg_id = match.group(1), int(match.group(2))
        
        if chat.isdigit() or chat.startswith("c/"):
            if f"-100{chat.replace('c/', '')}" == str(client.db_channel.id):
                return msg_id
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
    
