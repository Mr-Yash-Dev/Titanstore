import base64
import re
import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified
from config import FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, START_PIC
from database.database import is_admin, is_owner

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
    try:
        if message.photo or message.video or message.document:
            await message.edit_caption(caption=prompt, reply_markup=keyboard)
        else:
            if message.text != prompt: 
                await message.edit_text(text=prompt, reply_markup=keyboard)
    except MessageNotModified: pass
    except Exception: pass

    try:
        msg = await client.listen(message.chat.id, timeout=300)
        
        if not msg.text or msg.text.lower() == "/cancel":
            await msg.reply_photo(
                photo=START_PIC, 
                caption="❌ **Cancelled!**", 
                reply_markup=keyboard
            )
            return None
            
        return msg.text
        
    except asyncio.TimeoutError:
        await message.reply_photo(
            photo=START_PIC, 
            caption="⌛ **Timeout!**", 
            reply_markup=keyboard
        )
        return None

async def subscribed(client, message) -> bool:
    if not message.from_user: return True
    user_id = message.from_user.id
    if await is_admin(user_id) or await is_owner(user_id): return True
    for channel in [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]:
        if not channel or str(channel) in ["0", "-100"]: continue
        try:
            chat_id = int(channel) if str(channel).startswith("-100") or str(channel).isdigit() else channel
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
        except UserNotParticipant: return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                member = await client.get_chat_member(chat_id, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
            except: return False
        except Exception: continue
    return True

async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()

async def get_messages(client, message_ids):
    messages, total = [], 0
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
        return message.forward_from_message_id if message.forward_from_chat.id == client.db_channel.id else 0
    if message.forward_sender_name: return 0
    if message.text:
        match = re.search(r"https://t.me/(?:c/)?([^/]+)/(\d+)", message.text)
        if match:
            chat, msg_id = match.group(1), int(match.group(2))
            if chat in [str(client.db_channel.id), client.db_channel.username, f"-100{client.db_channel.id}".replace("-100-100", "-100")]: return msg_id
    return 0

def get_readable_time(seconds: int) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    res = []
    if days: res.append(f"{days}d")
    if hours: res.append(f"{hours}h")
    if minutes: res.append(f"{minutes}m")
    if seconds or not res: res.append(f"{seconds}s")
    return " ".join(res)
    
