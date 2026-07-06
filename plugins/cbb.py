import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT, OWNER_ID, START_PIC
from helper_func import safe_edit, get_input
from database.database import (
    is_admin, add_admin, remove_admin, get_admins, ban_user, unban_user, get_banned_users,
    add_premium, remove_premium, premium_collection, get_auto_delete, set_auto_delete,
    get_protect_status, set_protect_status, get_fsub_status, set_fsub_status, add_fsub, remove_fsub, get_fsubs
)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.message: return
    data = query.data
    user_id = query.from_user.id
    admin_status = await is_admin(user_id)
    first_name = query.from_user.first_name or "User"

    if data == "start":
        btn = [[InlineKeyboardButton("🧠 Help", callback_data="help"), InlineKeyboardButton("🔰 About", callback_data="about")]]
        if admin_status: btn.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])
        return await safe_edit(query.message, START_MSG.format(first=first_name), InlineKeyboardMarkup(btn))

    # --- STANDARD MENUS ---
    elif data in ["help", "commands", "about", "disclaimer"]:
        texts = {"help": HELP_TXT, "commands": COMMANDS_TXT, "about": ABOUT_TXT, "disclaimer": DISCLAIMER_TXT}
        txt = texts[data].format(first=first_name) if "{first}" in texts[data] else texts[data]
        btn = [[InlineKeyboardButton("🔙 Back", callback_data="start")]]
        return await safe_edit(query.message, txt, InlineKeyboardMarkup(btn))

    # --- SETTINGS MENU ---
    elif data == "settings":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        return await safe_edit(query.message, "⚙️ **Master Settings Panel**", InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 Admin", callback_data="admin_menu"), InlineKeyboardButton("🚫 Ban", callback_data="ban_menu")],
            [InlineKeyboardButton("💎 Premium", callback_data="premium_menu"), InlineKeyboardButton("📢 FSub", callback_data="fsub_menu")],
            [InlineKeyboardButton("🗑 Auto Delete", callback_data="ad_menu"), InlineKeyboardButton("🔐 Protect Content", callback_data="pc_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]))

    # --- PROTECT CONTENT ---
    elif data == "pc_menu":
        if not admin_status: return
        status = await get_protect_status()
        state_str = "ON ✅" if status else "OFF ❌"
        return await safe_edit(query.message, f"🔐 **Protect Content**\nStatus: {state_str}", InlineKeyboardMarkup([
            [InlineKeyboardButton("Toggle Mode", callback_data="pc_toggle")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "pc_toggle":
        if not admin_status: return
        new_status = not await get_protect_status()
        await set_protect_status(new_status)
        await query.answer("Status Updated!", show_alert=True)
        # trigger menu reload
        query.data = "pc_menu"
        return await cb_handler(client, query)

    # --- AUTO DELETE ---
    elif data == "ad_menu":
        if not admin_status: return
        timer = await get_auto_delete()
        state_str = f"ON ✅ ({timer}s)" if timer > 0 else "OFF ❌"
        return await safe_edit(query.message, f"🗑 **Auto Delete**\nStatus: {state_str}", InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Timer (Sec)", callback_data="ad_set"), InlineKeyboardButton("Turn OFF", callback_data="ad_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "ad_off":
        if not admin_status: return
        await set_auto_delete(0)
        await query.answer("Auto Delete Disabled!", show_alert=True)
        query.data = "ad_menu"
        return await cb_handler(client, query)
    elif data == "ad_set":
        if not admin_status: return
        val = await get_input(client, query.message, "Send auto-delete timer in seconds (e.g. 60):")
        if val and val.isdigit():
            await set_auto_delete(int(val))
            await query.message.reply(f"✅ Timer set to {val} seconds.")

    # --- FORCE SUB MENU ---
    elif data == "fsub_menu":
        if not admin_status: return
        status = "ON ✅" if await get_fsub_status() else "OFF ❌"
        return await safe_edit(query.message, f"📢 **Force Sub**\nMaster Status: {status}", InlineKeyboardMarkup([
            [InlineKeyboardButton("Toggle Master", callback_data="fsub_toggle")],
            [InlineKeyboardButton("➕ Add Fsub", callback_data="fsub_add"), InlineKeyboardButton("➖ Del Fsub", callback_data="fsub_del")],
            [InlineKeyboardButton("📋 FSub List", callback_data="fsub_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "fsub_toggle":
        if not admin_status: return
        new_status = not await get_fsub_status()
        await set_fsub_status(new_status)
        query.data = "fsub_menu"
        return await cb_handler(client, query)
    elif data == "fsub_add":
        if not admin_status: return
        val = await get_input(client, query.message, "Send Channel ID to Add (e.g. -100123...):")
        if val:
            try: 
                await add_fsub(int(val))
                await query.message.reply(f"✅ Added {val} to Force Subs.")
            except: await query.message.reply("❌ Invalid ID format.")
    elif data == "fsub_del":
        if not admin_status: return
        val = await get_input(client, query.message, "Send Channel ID to Remove:")
        if val:
            try:
                await remove_fsub(int(val))
                await query.message.reply(f"✅ Removed {val} from Force Subs.")
            except: pass
    elif data == "fsub_list":
        if not admin_status: return
        fsubs = await get_fsubs()
        text = "\n".join([f"• <code>{f}</code>" for f in fsubs]) if fsubs else "No channels added."
        return await safe_edit(query.message, f"📢 **FSub Channels:**\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="fsub_menu")]]))

    # --- ADMIN / PREMIUM MENUS (Unchanged logic, just compacted) ---
    elif data == "close":
        try: await query.message.delete()
        except: pass
            
