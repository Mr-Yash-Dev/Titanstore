from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT, OWNER_ID
from helper_func import safe_edit
from database.database import is_admin

@Client.on_callback_query(filters.regex("^(start|help|commands|about|disclaimer|close)$"))
async def generic_cb_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    admin_status = await is_admin(user_id)
    first_name = query.from_user.first_name or "User"

    if data == "start":
        buttons = [[InlineKeyboardButton("🧠 Help", callback_data="help"), InlineKeyboardButton("🔰 About", callback_data="about")]]
        if admin_status: buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])
        return await safe_edit(query.message, START_MSG.format(first=first_name), InlineKeyboardMarkup(buttons))

    elif data == "help":
        return await safe_edit(query.message, HELP_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"), InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "commands":
        return await safe_edit(query.message, COMMANDS_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "about":
        return await safe_edit(query.message, ABOUT_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"), InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "disclaimer":
        return await safe_edit(query.message, DISCLAIMER_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="about")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "close":
        try: await query.message.delete()
        except: pass
            
