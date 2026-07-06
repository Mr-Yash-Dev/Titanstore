from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import is_admin, get_auto_delete_status, set_auto_delete_status

@Client.on_callback_query(filters.regex(r"^autodelete_"))
async def autodelete_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Access Denied: Admins only!", show_alert=True)

    data = query.data

    if data == "autodelete_menu":
        is_on = await get_auto_delete_status()
        status = "ON ✅" if is_on else "OFF ❌"
        return await safe_edit(query.message, f"🗑 **Auto Delete Management**\n\nCurrent Status: **{status}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "autodelete_on":
        if await get_auto_delete_status():
            return await query.answer("⚠️ Auto Delete is already ON!", show_alert=True)
        await set_auto_delete_status(True)
        await query.answer("✅ Auto Delete Enabled!", show_alert=True)
        return await safe_edit(query.message, "🗑 **Auto Delete Management**\n\nCurrent Status: **ON ✅**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "autodelete_off":
        if not await get_auto_delete_status():
            return await query.answer("⚠️ Auto Delete is already OFF!", show_alert=True)
        await set_auto_delete_status(False)
        await query.answer("❌ Auto Delete Disabled!", show_alert=True)
        return await safe_edit(query.message, "🗑 **Auto Delete Management**\n\nCurrent Status: **OFF ❌**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
        
