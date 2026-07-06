
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import is_admin

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    # 🔒 STRICT ADMIN CHECK - Blocks normal users instantly
    if not await is_admin(user_id):
        await query.answer("⚠️ Admins only! You don't have permission.", show_alert=True)
        return  # This stops the menu from opening!

    return await safe_edit(query.message, "⚙️ Admin Settings Panel", InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"), InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("💎 Premium Menu", callback_data="premium_menu"), InlineKeyboardButton("🗑 Auto Delete", callback_data="autodelete_menu")],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ]))
    
