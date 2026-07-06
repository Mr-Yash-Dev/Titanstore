from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_input
from database.database import is_admin, add_premium, remove_premium, premium_collection

@Client.on_callback_query(filters.regex(r"^premium_"))
async def premium_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Admins only!", show_alert=True)
        
    data = query.data

    if data == "premium_menu":
        return await safe_edit(query.message, "💎 Premium Management\n\nPremium users can generate file links.", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Premium User", callback_data="premium_add")],
            [InlineKeyboardButton("➖ Remove Premium User", callback_data="premium_remove")],
            [InlineKeyboardButton("📋 Premium Member List", callback_data="premium_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "premium_add":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Premium Menu", callback_data="premium_menu")]])
        text = await get_input(client, query.message, "Send user_id and number of days (Space separated).\n\nExample: `123456789 30`", keyboard)
        if not text: return 
        parts = text.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit(): 
            return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid format. Use: `user_id days`", reply_markup=keyboard)
        uid, days = int(parts[0]), int(parts[1])
        await add_premium(uid, days)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid} has been granted Premium for {days} days.", reply_markup=keyboard)

    elif data == "premium_remove":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Premium Menu", callback_data="premium_menu")]])
        text = await get_input(client, query.message, "Send user_id to revoke Premium access", keyboard)
        if not text: return 
        if not text.isdigit(): 
            return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid User ID", reply_markup=keyboard)
        uid = int(text)
        await remove_premium(uid)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid}'s Premium access was revoked.", reply_markup=keyboard)

    elif data == "premium_list":
        cursor = premium_collection.find({"is_premium": True})
        users = await cursor.to_list(length=100)
        if not users: 
            return await safe_edit(query.message, "No premium users found.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="premium_menu")]]))
        
        text = ""
        for u in users:
            exp = u.get("expires_at")
            exp_str = exp.strftime('%Y-%m-%d UTC') if exp else "Never"
            text += f"• <code>{u['_id']}</code> (Expires: {exp_str})\n"
            
        return await safe_edit(query.message, f"💎 Premium Users:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="premium_menu")]]))
      
