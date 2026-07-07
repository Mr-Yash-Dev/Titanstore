import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserDeactivated
from database.database import is_admin, get_all_users

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Access Denied: Admins only!")
        
    if not message.reply_to_message:
        return await message.reply_text("Please reply to a message to broadcast it.")
        
    users = await get_all_users()
    b_msg = await message.reply_text(f"📡 Broadcasting message to {len(users)} users. Please wait...")
    
    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            successful += 1
            await asyncio.sleep(0.1)  # Stagger to prevent Telegram API limits
            
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                successful += 1
            except UserIsBlocked:
                blocked += 1
            except (UserDeactivated, InputUserDeactivated):
                deleted += 1
            except Exception:
                unsuccessful += 1
                
        except UserIsBlocked:
            blocked += 1
            
        except (UserDeactivated, InputUserDeactivated):
            deleted += 1
            
        except Exception:
            unsuccessful += 1
            
    # The new formatted status message
    status = f"""
<b>📢 Broadcast Completed</b>

<b>Total Users:</b> <code>{total}</code>
<b>Successful:</b> <code>{successful}</code>
<b>Blocked Users:</b> <code>{blocked}</code>
<b>Deleted Accounts:</b> <code>{deleted}</code>
<b>Unsuccessful:</b> <code>{unsuccessful}</code>
"""
    
    await b_msg.edit_text(status)
    
