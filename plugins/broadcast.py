import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from database.database import is_admin, user_data, delete_user

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("❌ Unauthorized.")
    if not message.reply_to_message:
        msg = await message.reply_text("❌ Reply to a message to broadcast.")
        await asyncio.sleep(8)
        try:
            await msg.delete()
            await message.delete()
        except: pass
        return

    pls_wait = await message.reply_text("📢 Broadcasting... Please wait...")
    total = await user_data.count_documents({})
    successful, blocked, deleted, unsuccessful = 0, 0, 0, 0

    async for user in user_data.find({}, {"_id": 1}):
        try:
            await message.reply_to_message.copy(user["_id"])
            successful += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user["_id"])
                successful += 1
            except: unsuccessful += 1
        except Exception as e:
            error = str(e).lower()
            if "blocked" in error: blocked += 1
            elif "deactivated" in error or "deleted" in error: 
                deleted += 1
                await delete_user(user["_id"])
            else: unsuccessful += 1

    status = f"<b>📢 Broadcast Completed</b>\n<b>Total:</b> <code>{total}</code>\n<b>Success:</b> <code>{successful}</code>\n<b>Blocked:</b> <code>{blocked}</code>\n<b>Deleted:</b> <code>{deleted}</code>\n<b>Failed:</b> <code>{unsuccessful}</code>"
    await pls_wait.edit_text(status, parse_mode=ParseMode.HTML)
  
