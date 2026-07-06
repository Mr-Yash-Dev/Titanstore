import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.database import is_admin, get_all_users

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Access Denied: Admins only!")
        
    if not message.reply_to_message:
        return await message.reply_text("Please reply to a message to broadcast it.")
        
    users = await get_all_users()
    b_msg = await message.reply_text(f"📡 Broadcasting message to {len(users)} users. Please wait...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            success += 1
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user_id)
            success += 1
        except (UserIsBlocked, InputUserDeactivated, Exception):
            failed += 1
            
    await b_msg.edit_text(f"✅ **Broadcast Completed**\n\n🎯 **Total Users:** {len(users)}\n✅ **Successful:** {success}\n❌ **Failed:** {failed}")
    
