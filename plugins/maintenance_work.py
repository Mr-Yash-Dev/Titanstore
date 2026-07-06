from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import maintenance_collection, is_admin

@Client.on_message(filters.command("maintenance") & filters.private)
async def maintenance_toggle_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return

    if len(message.command) != 2: return await message.reply_text("<b>Usage:</b>\n`/maintenance on`\n`/maintenance off`")
    arg = message.command[1].lower()
    if arg not in ("on", "off"): return await message.reply_text("❌ Use `on` or `off`.")

    await maintenance_collection.update_one({"_id": "maintenance"}, {"$set": {"maintenance": arg}}, upsert=True)
    if arg == "on": await message.reply_text("✅ Maintenance ON.")
    else: await message.reply_text("⚙️ Maintenance OFF.")
        
