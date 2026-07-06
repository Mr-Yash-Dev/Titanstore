from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC, OWNER_ID
from helper_func import safe_edit, get_input
from database.database import is_admin, add_admin, remove_admin, get_admins

@Client.on_callback_query(filters.regex(r"^admin_"))
async def admin_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Access Denied: Admin Menu is restricted!", show_alert=True)
    
    data = query.data

    if data == "admin_menu":
        return await safe_edit(query.message, "👨‍💻 Admin Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Admin", callback_data="admin_add"), InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove")],
            [InlineKeyboardButton("📋 Admin List", callback_data="admin_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "admin_add":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]])
        text = await get_input(client, query.message, "Send user_id to add as admin", keyboard)
        if not text: return 
        if not text.isdigit(): return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid ID", reply_markup=keyboard)
        uid = int(text)
        if uid == int(OWNER_ID): return await query.message.reply_photo(photo=START_PIC, caption="⚠️ Owner is already admin", reply_markup=keyboard)
        await add_admin(uid)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid} added as admin", reply_markup=keyboard)

    elif data == "admin_remove":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]])
        text = await get_input(client, query.message, "Send user_id to remove from admin", keyboard)
        if not text: return 
        if not text.isdigit(): return await query.message.reply_photo(photo=START_PIC, caption="❌ Invalid ID", reply_markup=keyboard)
        uid = int(text)
        if uid == int(OWNER_ID): return await query.message.reply_photo(photo=START_PIC, caption="❌ Cannot remove owner", reply_markup=keyboard)
        await remove_admin(uid)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ User {uid} removed from admin", reply_markup=keyboard)

    elif data == "admin_list":
        admins = await get_admins()
        if not admins: return await safe_edit(query.message, "No admins found.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))
        text = "\n".join([f"• {a}" for a in admins[:100]])
        return await safe_edit(query.message, f"👨‍💻 Admin List:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))
        
