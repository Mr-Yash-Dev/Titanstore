from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit, get_input, get_readable_time
from database.database import is_admin, get_auto_delete_status, set_auto_delete_status, get_auto_delete_time, set_auto_delete_time

def parse_time(time_str: str) -> int:
    """Converts user input like '1h' or '15m' into total seconds."""
    time_str = time_str.lower().strip()
    if time_str.endswith('h') and time_str[:-1].isdigit(): 
        return int(time_str[:-1]) * 3600
    elif time_str.endswith('m') and time_str[:-1].isdigit(): 
        return int(time_str[:-1]) * 60
    elif time_str.endswith('s') and time_str[:-1].isdigit(): 
        return int(time_str[:-1])
    elif time_str.isdigit(): 
        return int(time_str)
    return 0

@Client.on_callback_query(filters.regex(r"^autodelete_"))
async def autodelete_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ Access Denied: Admins only!", show_alert=True)
    
    data = query.data

    if data == "autodelete_menu":
        is_on = await get_auto_delete_status()
        status = "ON ✅" if is_on else "OFF ❌"
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 **Auto Delete Management**\n\nCurrent Status: **{status}**\nDelete Time: **{get_readable_time(current_time)}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("⏱ Change Timer", callback_data="autodelete_set_time")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
        
    elif data == "autodelete_on":
        await set_auto_delete_status(True)
        await query.answer("✅ Auto Delete Enabled!", show_alert=True)
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 **Auto Delete Management**\n\nCurrent Status: **ON ✅**\nDelete Time: **{get_readable_time(current_time)}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("⏱ Change Timer", callback_data="autodelete_set_time")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
        
    elif data == "autodelete_off":
        await set_auto_delete_status(False)
        await query.answer("❌ Auto Delete Disabled!", show_alert=True)
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 **Auto Delete Management**\n\nCurrent Status: **OFF ❌**\nDelete Time: **{get_readable_time(current_time)}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="autodelete_on"), InlineKeyboardButton("❌ Disable", callback_data="autodelete_off")],
            [InlineKeyboardButton("⏱ Change Timer", callback_data="autodelete_set_time")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
        
    elif data == "autodelete_set_time":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="autodelete_menu")]])
        prompt_text = "<b>SEND ME A TIME IN LIKE THIS - 1h OR 15m\n\n/cancel - CANCEL THIS PROCESS.</b>"
        
        # 1. Ask the user in the chat for the time
        text = await get_input(client, query.message, prompt_text, keyboard)
        if not text: return 
        
        # 2. Convert their message to seconds
        time_in_seconds = parse_time(text)
        if time_in_seconds < 10: 
            return await query.message.reply("❌ **Invalid format!** Please use formats like `1h`, `15m`, or `30s`.", quote=True)
            
        # 3. Save it to the database
        await set_auto_delete_time(time_in_seconds)
        
        # 4. Confirm success
        await query.message.reply(f"✅ Auto-delete timer successfully set to **{get_readable_time(time_in_seconds)}**.", quote=True)
        
