import os
import logging
from logging.handlers import RotatingFileHandler

def get_env_int(env_key, default_value):
    val = os.environ.get(env_key)
    return int(val) if val else default_value

def get_env_list(env_key):
    val = os.environ.get(env_key, "")
    return [int(i) for i in val.split() if i.strip().isdigit()]

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8879094453:AAF3akfIR6UO9eMxriVnlKq8LbK2a6TkQ3s")
APP_ID = get_env_int("APP_ID", 12293838)
API_HASH = os.environ.get("API_HASH", "cf8c7db0d609148786e7ca5c706909bd")

CHANNEL_ID = get_env_int("CHANNEL_ID", -1002096962621)
LOG_CHANNEL_ID = get_env_int("LOG_CHANNEL_ID", -1002313688533)
OWNER_ID = get_env_int("OWNER_ID", 5356695781)
PORT = get_env_int("PORT", 8080)
TG_BOT_WORKERS = get_env_int("TG_BOT_WORKERS", 4)
ADMINS = get_env_list("ADMINS", 5356695781) # Space separated Admin IDs in environment

DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://TITANBOTS:TITANBOTS@cluster0.yagdfyt.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "TitanBot")

START_PIC = os.environ.get("START_PIC", "https://envs.sh/WeX.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://envs.sh/TPh.jpg")

# --- COMBINED SCRIPT TEXTS ---
HELP_TXT = "<b>ᴛʜɪs ɪs ᴀɴ ꜰɪʟᴇꜱᴛᴏʀᴇ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @TitanCineplex\n\n sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴏɴ ʟɪɴᴋ ᴀɴᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴊᴏɪɴ 🫵 ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ!</b>"
ABOUT_TXT = "<b>✯ ᴄʀᴇᴀᴛᴏʀ : <a href=https://t.me/TitanXBots>ᎩᎪᏚʜཛ</a>\n✯ ʟᴀɴɢᴜᴀɢᴇ : ᴘʏᴛʜᴏɴ3\n✯ ʟɪʙʀᴀʀʏ : ᴘʏʀᴏɢʀᴀᴍ\n✯ ꜱᴏᴜʀᴄᴇ : ᴘʀɪᴠᴀᴛᴇ\n✯ ᴜᴘᴅᴀᴛᴇꜱ : <a href=https://t.me/TitanXBots>ᴛɪᴛᴀɴxʙᴏᴛꜱ</a></b>"
COMMANDS_TXT = "<b>🤖 Bot Commands Menu</b>\n\n• /start - Initialize\n• /batch - Multi-link Generator\n• /genlink - Single-link\n• Click ⚙️ Settings on /start panel to modify bot."
DISCLAIMER_TXT = "<b>⚠️ Disclaimer Notice</b>\n\nThis bot is strictly meant for sharing personal storage files. We respect all DMCA laws."
START_MSG = os.environ.get("START_MESSAGE", "ʜᴇʟʟᴏ {first}\n\nɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ꜰɪʟᴇꜱ ɪɴ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ɪᴛ ꜰʀᴏᴍ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋ.")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ(ꜱ) ᴛᴏ ᴜꜱᴇ ᴍᴇ\n\nᴋɪɴᴅʟʏ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ</b>")
USER_REPLY_TEXT = "👋 ʜᴇʏ ꜰʀɪᴇɴᴅ, 🚫 ᴅᴏɴ'ᴛ ꜱᴇɴᴅ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴍᴇ ᴅɪʀᴇᴄᴛʟʏ!"

BOT_STATS_TEXT = """<b>📊 Bot Uptime Metrics</b>

⏱ **Uptime:** {uptime}
👥 **Total Users:** {tot_users}
👨‍💻 **Total Admins:** {tot_admins}
🚫 **Banned Users:** {tot_banned}
💎 **Premium Users:** {tot_premium}

⚙️ <b>Settings Status:</b>
📢 **Force Sub Mode:** {fsub_stat} (Channels: {tot_fsub})
🗑 **Auto-Delete Mode:** {ad_stat}
🔐 **Protect Content:** {pc_stat}"""

LOG_FILE_NAME = "filesharingbot.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    handlers=[RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10), logging.StreamHandler()]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
    
