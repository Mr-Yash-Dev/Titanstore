import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT, OWNER_ID, START_PIC
from helper_func import safe_edit, get_input
from database.database import (
    is_admin, add_admin, remove_admin, get_admins, ban_user, unban_user, get_banned_users,
    add_premium, remove_premium, premium_collection, get_settings, update_settings, 
    get_fsub_channels, add_fsub_channel, remove_fsub_channel
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
        buttons = [[InlineKeyboardButton("🧠 Help", callback_data="help"), InlineKeyboardButton("🔰 About", callback_data="about")]]
        if admin_status: buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])
        return await safe_edit(query.message, START_MSG.format(first=first_name), InlineKeyboardMarkup(buttons))

    elif data == "help":
        return await safe_edit(query.message, HELP_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "commands":
        return await safe_edit(query.message, COMMANDS_TXT, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help")]]))

    elif data == "about":
        return await safe_edit(query.message, ABOUT_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")]
        ]))

    elif data == "disclaimer":
        return await safe_edit(query.message, DISCLAIMER_TXT, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="about")]]))

    elif data == "settings":
        if not admin_status: return
        return await safe_edit(query.message, "⚙️ Admin Settings Panel", InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 Admins", callback_data="admin_menu"), InlineKeyboardButton("🚫 Bans", callback_data="ban_menu")],
            [InlineKeyboardButton("💎 Premium", callback_data="premium_menu"), InlineKeyboardButton("📢 F-Sub", callback_data="fsub_menu")],
            [InlineKeyboardButton("🗑 Auto Delete", callback_data="autodelete_menu"), InlineKeyboardButton("🔐 Protect", callback_data="protect_menu")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")]
        ]))

    # --- Protect Content ---
    elif data == "protect_menu":
        if not admin_status: return
        settings = await get_settings()
        status = "ON ✅" if settings.get("protect_content") else "OFF ❌"
        return await safe_edit(query.message, f"🔐 **Protect Content Mode**\nCurrent: **{status}**\n\nPrevents users from forwarding or saving media.", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Enable", callback_data="protect_on"), InlineKeyboardButton("❌ Disable", callback_data="protect_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data in ["protect_on", "protect_off"]:
        if not admin_status: return
        await update_settings("protect_content", data == "protect_on")
        await query.answer("Status Updated!", show_alert=True)
        query.data = "protect_menu"
        return await cb_handler(client, query)

    # --- Auto Delete ---
    elif data == "autodelete_menu":
        if not admin_status: return
        settings = await get_settings()
        status = "ON ✅" if settings.get("auto_delete") else "OFF ❌"
        timer = settings.get("auto_delete_timer", 60)
        return await safe_edit(query.message, f"🗑 **Auto Delete Management**\n\nStatus: **{status}**\nTimer: **{timer} seconds**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ON", callback_data="del_on"), InlineKeyboardButton("❌ OFF", callback_data="del_off")],
            [InlineKeyboardButton("⏱ Set Timer", callback_data="del_timer")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data in ["del_on", "del_off"]:
        if not admin_status: return
        await update_settings("auto_delete", data == "del_on")
        await query.answer("Status Updated!", show_alert=True)
        query.data = "autodelete_menu"
        return await cb_handler(client, query)
    elif data == "del_timer":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="autodelete_menu")]])
        val = await get_input(client, query.message, "Send new timer in seconds (e.g. 300 for 5 mins):", keyboard)
        if val and val.isdigit():
            await update_settings("auto_delete_timer", int(val))
            await query.message.reply("✅ Timer updated!")
            
    # --- Force Sub ---
    elif data == "fsub_menu":
        if not admin_status: return
        settings = await get_settings()
        status = "ON ✅" if settings.get("fsub_mode") else "OFF ❌"
        return await safe_edit(query.message, f"📢 **Force Subscribe**\nMode: **{status}**", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Mode ON", callback_data="fsub_on"), InlineKeyboardButton("❌ Mode OFF", callback_data="fsub_off")],
            [InlineKeyboardButton("➕ Add Ch.", callback_data="addfsub"), InlineKeyboardButton("➖ Del Ch.", callback_data="delfsub")],
            [InlineKeyboardButton("📋 Ch. List", callback_data="fsublist"), InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data in ["fsub_on", "fsub_off"]:
        if not admin_status: return
        await update_settings("fsub_mode", data == "fsub_on")
        await query.answer("Status Updated!", show_alert=True)
        query.data = "fsub_menu"
        return await cb_handler(client, query)
    elif data == "addfsub":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="fsub_menu")]])
        val = await get_input(client, query.message, "Send Channel ID (must start with -100):", keyboard)
        if val:
            try:
                await add_fsub_channel(int(val))
                await client.fetch_fsub_links()
                await query.message.reply("✅ Channel added to Force Sub!")
            except ValueError:
                await query.message.reply("❌ Invalid Channel ID format.")
    elif data == "delfsub":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="fsub_menu")]])
        val = await get_input(client, query.message, "Send Channel ID to remove:", keyboard)
        if val:
            try:
                await remove_fsub_channel(int(val))
                await client.fetch_fsub_links()
                await query.message.reply("✅ Channel removed from Force Sub!")
            except ValueError:
                await query.message.reply("❌ Invalid Channel ID format.")
    elif data == "fsublist":
        if not admin_status: return
        channels = await get_fsub_channels()
        text = "\n".join([f"• <code>{ch}</code>" for ch in channels]) if channels else "None"
        return await safe_edit(query.message, f"📢 **F-Sub Channels:**\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="fsub_menu")]]))

    # --- Admin Management ---
    elif data == "admin_menu":
        if not admin_status: return
        return await safe_edit(query.message, "👨‍💻 Admin Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"), InlineKeyboardButton("➖ Del Admin", callback_data="remove_admin")],
            [InlineKeyboardButton("📋 List", callback_data="admin_list"), InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "add_admin":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="admin_menu")]])
        val = await get_input(client, query.message, "Send User ID to add as admin:", keyboard)
        if val and val.isdigit():
            await add_admin(int(val))
            await query.message.reply("✅ Admin added successfully!")
    elif data == "remove_admin":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="admin_menu")]])
        val = await get_input(client, query.message, "Send User ID to remove from admin:", keyboard)
        if val and val.isdigit():
            if int(val) == OWNER_ID:
                return await query.message.reply("❌ You cannot remove the Owner.")
            await remove_admin(int(val))
            await query.message.reply("✅ Admin removed successfully!")
    elif data == "admin_list":
        if not admin_status: return
        admins = await get_admins()
        text = "\n".join([f"• <code>{a}</code>" for a in admins[:100]]) if admins else "No additional database admins."
        return await safe_edit(query.message, f"👨‍💻 **Admin List:**\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))

    # --- Ban Management ---
    elif data == "ban_menu":
        if not admin_status: return
        return await safe_edit(query.message, "🚫 Ban Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Ban", callback_data="ban_user"), InlineKeyboardButton("✅ Unban", callback_data="unban_user")],
            [InlineKeyboardButton("📋 List", callback_data="banned_list"), InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "ban_user":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="ban_menu")]])
        val = await get_input(client, query.message, "Send User ID and Reason (e.g. `123456 spamming`):", keyboard)
        if val:
            parts = val.split(maxsplit=1)
            if parts[0].isdigit():
                reason = parts[1] if len(parts) > 1 else "No reason"
                await ban_user(int(parts[0]), reason)
                await query.message.reply("✅ User banned!")
    elif data == "unban_user":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="ban_menu")]])
        val = await get_input(client, query.message, "Send User ID to unban:", keyboard)
        if val and val.isdigit():
            await unban_user(int(val))
            await query.message.reply("✅ User unbanned!")
    elif data == "banned_list":
        if not admin_status: return
        banned = await get_banned_users()
        text = "\n".join([f"• <code>{u['_id']}</code> - {u.get('reason', 'N/A')}" for u in banned[:100]]) if banned else "No banned users."
        return await safe_edit(query.message, f"🚫 **Banned Users:**\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))

    # --- Premium Management ---
    elif data == "premium_menu":
        if not admin_status: return
        return await safe_edit(query.message, "💎 Premium Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add", callback_data="addpremiumuser"), InlineKeyboardButton("➖ Remove", callback_data="removepremiumuser")],
            [InlineKeyboardButton("📋 List", callback_data="premium_member_list"), InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    elif data == "addpremiumuser":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="premium_menu")]])
        val = await get_input(client, query.message, "Send User ID and Days (e.g. `123456 30`):", keyboard)
        if val:
            parts = val.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                await add_premium(int(parts[0]), int(parts[1]))
                await query.message.reply(f"✅ Premium added for {parts[1]} days!")
            else:
                await query.message.reply("❌ Invalid format.")
    elif data == "removepremiumuser":
        if not admin_status: return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="premium_menu")]])
        val = await get_input(client, query.message, "Send User ID to remove premium:", keyboard)
        if val and val.isdigit():
            await remove_premium(int(val))
            await query.message.reply("✅ Premium removed!")
    elif data == "premium_member_list":
        if not admin_status: return
        cursor = premium_collection.find({"is_premium": True})
        users = await cursor.to_list(length=100)
        text = "\n".join([f"• <code>{u['_id']}</code>" for u in users]) if users else "No premium users."
        return await safe_edit(query.message, f"💎 **Premium Users:**\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="premium_menu")]]))

    # --- Close Menu ---
    elif data == "close":
        try: await query.message.delete()
        except: pass
            
