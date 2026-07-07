from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import is_admin, get_protect_status, set_protect_status

@Client.on_callback_query(filters.regex("^(settings|protect_menu|protect_on|protect_off)$"))
async def settings_cb(client: Client, query: CallbackQuery):
    # 🔒 STRICT LOCK: Admins Only for everything in this file
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Access Denied: Settings are for Admins only!", show_alert=True)
        
    data = query.data

    # --- Main Settings Menu ---
    if data == "settings":
        return await safe_edit(query.message, "⚙️ Admin Settings Panel", InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"), InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("💎 Premium Menu", callback_data="premium_menu"), InlineKeyboardButton("🗑 Auto Delete", callback_data="autodelete_menu")],
            [InlineKeyboardButton("🔒 Protect Content", callback_data="protect_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]))

    # --- Protect Content Menu ---
    elif data == "protect_menu":
        is_on = await get_protect_status()
        status = "ON ✅" if is_on else "OFF ❌"
        return await safe_edit(query.message, f"🔒 **Protect Content Management**\n\nPrevents users from forwarding, saving, or copying files.\n\nCurrent Status: **{status}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="protect_on"), InlineKeyboardButton("❌ Disable", callback_data="protect_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "protect_on":
        if await get_protect_status():
            return await query.answer("⚠️ Protect Content is already ON!", show_alert=True)
        await set_protect_status(True)
        await query.answer("✅ Protect Content Enabled!", show_alert=True)
        return await safe_edit(query.message, "🔒 **Protect Content Management**\n\nPrevents users from forwarding, saving, or copying files.\n\nCurrent Status: **ON ✅**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="protect_on"), InlineKeyboardButton("❌ Disable", callback_data="protect_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "protect_off":
        if not await get_protect_status():
            return await query.answer("⚠️ Protect Content is already OFF!", show_alert=True)
        await set_protect_status(False)
        await query.answer("❌ Protect Content Disabled!", show_alert=True)
        return await safe_edit(query.message, "🔒 **Protect Content Management**\n\nPrevents users from forwarding, saving, or copying files.\n\nCurrent Status: **OFF ❌**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="protect_on"), InlineKeyboardButton("❌ Disable", callback_data="protect_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
        
