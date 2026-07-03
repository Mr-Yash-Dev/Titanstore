import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import *
from helper_func import safe_edit, get_input
from database.database import (
    is_admin, add_admin, remove_admin, get_admins, ban_user, unban_user, get_banned_users,
    add_premium, remove_premium
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
            [InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"), InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "commands":
        return await safe_edit(query.message, COMMANDS_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "about":
        return await safe_edit(query.message, ABOUT_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"), InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "disclaimer":
        return await safe_edit(query.message, DISCLAIMER_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="about")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"), InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    elif data == "settings":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        return await safe_edit(query.message, "⚙️ Admin Settings Panel", InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"), InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("💎 Premium Menu", callback_data="premium_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]))

    elif data == "admin_menu":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        return await safe_edit(query.message, "👨‍💻 Admin Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"), InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")],
            [InlineKeyboardButton("📋 Admin List", callback_data="admin_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "add_admin":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id to add as admin")
        if not text or not text.isdigit(): return await safe_edit(query.message, "❌ Invalid User ID")
        uid = int(text)
        if uid == OWNER_ID: return await query.message.reply("⚠️ Owner is already admin")
        await add_admin(uid)
        await query.message.reply(f"✅ User {uid} added as admin")

    elif data == "remove_admin":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id to remove from admin")
        if not text or not text.isdigit(): return await safe_edit(query.message, "❌ Invalid User ID")
        uid = int(text)
        if uid == OWNER_ID: return await query.message.reply("❌ Cannot remove owner")
        await remove_admin(uid)
        await query.message.reply(f"✅ User {uid} removed from admin")

    elif data == "admin_list":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        admins = await get_admins()
        if not admins: return await safe_edit(query.message, "No admins found.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))
        text = "\n".join([f"• {a}" for a in admins])
        return await safe_edit(query.message, f"👨‍💻 Admin List:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))

    elif data == "ban_menu":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        return await safe_edit(query.message, "🚫 Ban Management", InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"), InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("📄 Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "ban_user":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id [reason]")
        if not text: return
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit(): return await safe_edit(query.message, "❌ Invalid User ID")
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"
        await ban_user(uid, reason)
        await query.message.reply(f"✅ User {uid} banned")

    elif data == "unban_user":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit(): return await safe_edit(query.message, "❌ Invalid User ID")
        uid = int(text)
        await unban_user(uid)
        await query.message.reply(f"✅ User {uid} unbanned")

    elif data == "banned_list":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        banned = await get_banned_users()
        if not banned: return await safe_edit(query.message, "No banned users.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))
        text = "\n".join([f"• {u['_id']} - {u.get('reason','No reason')}" for u in banned])
        return await safe_edit(query.message, f"🚫 Banned Users:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))

    elif data == "premium_menu":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        return await safe_edit(query.message, "💎 Premium Management\n\nPremium users can generate file links.", InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Premium User", callback_data="addpremiumuser")],
            [InlineKeyboardButton("➖ Remove Premium User", callback_data="removepremiumuser")],
            [InlineKeyboardButton("📋 Premium Member List", callback_data="premium_member_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    elif data == "addpremiumuser":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id and number of days (Space separated).\n\nExample: `123456789 30`")
        if not text: return
        parts = text.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit(): 
            return await safe_edit(query.message, "❌ Invalid format. Use: `user_id days`")
        uid, days = int(parts[0]), int(parts[1])
        await add_premium(uid, days)
        await query.message.reply(f"✅ User {uid} has been granted Premium for {days} days.")

    elif data == "removepremiumuser":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        text = await get_input(client, query.message, "Send user_id to revoke Premium access")
        if not text or not text.isdigit(): return await safe_edit(query.message, "❌ Invalid User ID")
        uid = int(text)
        await remove_premium(uid)
        await query.message.reply(f"✅ User {uid}'s Premium access was revoked.")

    elif data == "premium_member_list":
        if not admin_status: return await query.answer("⚠️ Admins only!", show_alert=True)
        from database.database import premium_collection
        cursor = premium_collection.find({"is_premium": True})
        users = await cursor.to_list(length=None)
        if not users: 
            return await safe_edit(query.message, "No premium users found.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="premium_menu")]]))
        text = ""
        for u in users:
            exp = u.get("expires_at")
            exp_str = exp.strftime('%Y-%m-%d') if exp else "Never"
            text += f"• <code>{u['_id']}</code> (Expires: {exp_str})\n"
        return await safe_edit(query.message, f"💎 Premium Users:\n\n{text}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="premium_menu")]]))

    elif data == "close":
        try: await query.message.delete()
        except: pass
            
