from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import maintenance_collection, is_admin

@Client.on_message(filters.command("maintenance") & filters.private)
async def maintenance_toggle(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    if len(message.command) != 2 or message.command[1].lower() not in ("on", "off"):
        return await message.reply_text("<b>Usage:</b>\n`/maintenance on` or `/maintenance off`")

    arg = message.command[1].lower()
    await maintenance_collection.update_one({"_id": "maintenance"}, {"$set": {"maintenance": arg}}, upsert=True)
    await message.reply_text(f"✅ Maintenance mode {arg.upper()}.")
    
