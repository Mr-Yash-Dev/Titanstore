from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_input
from database.database import is_admin, ban_user, unban_user, get_banned_users

@Client.on_callback_query(filters.regex(r"^ban_"))
async def ban_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Admins only!", show_alert=True)
    
    data = query.data

    if data == "ban_menu":
        return await safe_edit(query.message, "🚫 Ban Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"), InlineKeyboardButton("✅ Unban User", callback_data="ban_unban_user")],
            [InlineKeyboardButton("📄 Banned List", callback_data="ban_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "ban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Ban Menu", callback_data="ban_menu")]])
        text = await get_input(client, query.message, "Send user_id [reason]", keyboard)
        if not text: return 
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit(): 
            return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid User ID", reply_markup=keyboard)
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"
        await ban_user(uid, reason)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid} banned", reply_markup=keyboard)

    elif data == "ban_unban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Ban Menu", callback_data="ban_menu")]])
        text = await get_input(client, query.message, "Send user_id", keyboard)
        if not text: return 
        if not text.isdigit(): 
            return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid User ID", reply_markup=keyboard)
        uid = int(text)
        await unban_user(uid)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid} unbanned", reply_markup=keyboard)

    elif data == "ban_list":
        banned = await get_banned_users()
        if not banned: 
            return await safe_edit(query.message, "No banned users.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))
        text = "\n".join([f"• {u['_id']} - {u.get('reason','No reason')}" for u in banned[:100]])
        return await safe_edit(query.message, f"🚫 Banned Users:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))
      
