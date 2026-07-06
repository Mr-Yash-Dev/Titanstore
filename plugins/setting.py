from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import is_admin

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_cb(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Admins only!", show_alert=True)
        
    return await safe_edit(query.message, "⚙️ Admin Settings Panel", InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"), InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("💎 Premium Menu", callback_data="premium_menu"), InlineKeyboardButton("🗑 Auto Delete", callback_data="autodelete_menu")],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ]))
  
