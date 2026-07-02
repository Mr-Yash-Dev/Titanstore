from pyrogram import filters
from pyrogram.types import Message

from bot import Bot
from database.database import maintenance_collection, is_admin, is_owner


@Bot.on_message(filters.command("maintenance") & filters.private)
async def maintenance_toggle_command(client: Bot, message: Message):
    user_id = message.from_user.id

    # Only Owner can toggle maintenance
    if not await is_owner(user_id):
        if not await is_admin(user_id):
            return

    if len(message.command) != 2:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/maintenance on</code>\n"
            "<code>/maintenance off</code>"
        )

    arg = message.command[1].strip().lower()

    if arg not in ("on", "off"):
        return await message.reply_text(
            "❌ Invalid argument.\n\nUse only:\n"
            "<code>/maintenance on</code>\n"
            "<code>/maintenance off</code>"
        )

    try:
        await maintenance_collection.update_one(
            {"_id": "maintenance"},
            {"$set": {"maintenance": arg}},
            upsert=True
        )
    except Exception as e:
        return await message.reply_text(
            f"❌ Failed to update maintenance status.\n\n<code>{e}</code>"
        )

    if arg == "on":
        await message.reply_text(
            "✅ <b>Maintenance Mode Enabled</b>\n\n"
            "Non-admin users will not be able to use the bot."
        )
    else:
        await message.reply_text(
            "✅ <b>Maintenance Mode Disabled</b>\n\n"
            "Bot is now available for everyone."
        )
