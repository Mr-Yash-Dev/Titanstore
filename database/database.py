import motor.motor_asyncio
from datetime import datetime, timedelta, timezone
from config import DB_URI, DB_NAME, ADMINS, OWNER_ID

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
premium_collection = database["premium_users"]
settings_collection = database["settings"]

# -- Users --
async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def add_user(user_id: int, first_name=None, username=None):
    await user_data.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username, "joined_at": datetime.now(timezone.utc)}}, upsert=True)

async def delete_user(user_id: int):
    await user_data.delete_one({"_id": user_id})

async def get_total_users():
    return await user_data.count_documents({})

# -- Bans --
async def is_user_banned(user_id: int) -> bool:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("is_banned", False) if data else False

async def get_ban_reason(user_id: int) -> str:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"

async def ban_user(user_id: int, reason: str = "No reason"):
    await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": True, "reason": reason}}, upsert=True)

async def unban_user(user_id: int):
    await banned_users.delete_one({"_id": user_id})

async def get_banned_users():
    cursor = banned_users.find({"is_banned": True})
    return await cursor.to_list(length=None)

async def get_total_banned():
    return await banned_users.count_documents({"is_banned": True})

# -- Admins --
async def add_admin(user_id: int):
    await admins_collection.update_one({"_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)

async def remove_admin(user_id: int):
    await admins_collection.delete_one({"_id": user_id})

async def get_admins():
    cursor = admins_collection.find({}, {"_id": 1})
    admins = await cursor.to_list(length=None)
    return [admin["_id"] for admin in admins]

async def get_total_admins():
    return await admins_collection.count_documents({}) + len(ADMINS)

async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

async def is_admin(user_id: int) -> bool:
    if user_id in ADMINS: return True
    data = await admins_collection.find_one({"_id": user_id})
    return data is not None and data.get("is_admin", False)

# -- Premium --
async def add_premium(user_id: int, days: int):
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    await premium_collection.update_one({"_id": user_id}, {"$set": {"is_premium": True, "expires_at": expires_at, "notified": False}}, upsert=True)

async def remove_premium(user_id: int):
    await premium_collection.delete_one({"_id": user_id})

async def get_total_premium():
    return await premium_collection.count_documents({"is_premium": True})

async def is_premium(user_id: int) -> bool:
    if await is_admin(user_id): return True
    data = await premium_collection.find_one({"_id": user_id})
    if data and data.get("is_premium"):
        expires_at = data.get("expires_at")
        if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
            await remove_premium(user_id)
            return False
        return True
    return False

# -- Maintenance --
async def is_maintenance(user_id: int) -> bool:
    if await is_admin(user_id): return False
    data = await maintenance_collection.find_one({"_id": "maintenance"})
    return data is not None and data.get("maintenance") == "on"

# -- Dynamic Settings --
async def get_settings():
    default = {"auto_delete": True, "auto_delete_timer": 60, "protect_content": False, "fsub_mode": False, "fsub_channels": []}
    data = await settings_collection.find_one({"_id": "bot_settings"})
    if not data:
        await settings_collection.insert_one({"_id": "bot_settings", **default})
        return default
    return data

async def update_settings(key: str, value):
    await settings_collection.update_one({"_id": "bot_settings"}, {"$set": {key: value}}, upsert=True)

async def get_fsub_channels():
    settings = await get_settings()
    return settings.get("fsub_channels", [])

async def add_fsub_channel(channel_id: int):
    await settings_collection.update_one({"_id": "bot_settings"}, {"$addToSet": {"fsub_channels": channel_id}}, upsert=True)

async def remove_fsub_channel(channel_id: int):
    await settings_collection.update_one({"_id": "bot_settings"}, {"$pull": {"fsub_channels": channel_id}}, upsert=True)
    
