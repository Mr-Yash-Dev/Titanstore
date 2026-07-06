import motor.motor_asyncio
from datetime import datetime, timedelta, timezone
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
premium_collection = database["premium_users"]
settings_collection = database["settings"]

async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def add_user(user_id: int, first_name=None, username=None):
    await user_data.update_one(
        {"_id": user_id},
        {"$set": {"first_name": first_name, "username": username, "joined_at": datetime.now(timezone.utc)}},
        upsert=True
    )

async def get_all_users():
    cursor = user_data.find({}, {"_id": 1})
    users = await cursor.to_list(length=None)
    return [user["_id"] for user in users]

async def delete_user(user_id: int):
    await user_data.delete_one({"_id": user_id})

async def is_user_banned(user_id: int) -> bool:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("is_banned", False) if data else False

async def get_ban_reason(user_id: int) -> str:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"

async def ban_user(user_id: int, reason: str = "No reason"):
    await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": True, "reason": reason}}, upsert=True)

async def unban_user(user_id: int):
    await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": False, "reason": ""}}, upsert=True)

async def get_banned_users():
    cursor = banned_users.find({"is_banned": True})
    return await cursor.to_list(length=None)

async def add_admin(user_id: int):
    await admins_collection.update_one({"_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)

async def remove_admin(user_id: int):
    await admins_collection.delete_one({"_id": user_id})

async def get_admins():
    cursor = admins_collection.find({}, {"_id": 1})
    admins = await cursor.to_list(length=None)
    return [admin["_id"] for admin in admins]

async def is_owner(user_id: int) -> bool:
    try:
        return int(user_id) == int(OWNER_ID)
    except (ValueError, TypeError):
        return False

async def is_admin(user_id) -> bool:
    try:
        uid = int(user_id)
        if uid == int(OWNER_ID) or uid in ADMINS: 
            return True
            
        data = await admins_collection.find_one({"_id": uid})
        return data is not None and data.get("is_admin", False)
    except (ValueError, TypeError):
        return False

async def add_premium(user_id: int, days: int):
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    await premium_collection.update_one(
        {"_id": user_id}, 
        {"$set": {"is_premium": True, "expires_at": expires_at, "notified": False}}, 
        upsert=True
    )

async def remove_premium(user_id: int):
    await premium_collection.delete_one({"_id": user_id})

async def get_premium_users():
    cursor = premium_collection.find({}, {"_id": 1})
    users = await cursor.to_list(length=None)
    return [user["_id"] for user in users]

async def is_premium(user_id: int) -> bool:
    if await is_admin(user_id): return True
    
    try:
        uid = int(user_id)
        data = await premium_collection.find_one({"_id": uid})
        if data and data.get("is_premium"):
            expires_at = data.get("expires_at")
            if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
                await remove_premium(uid)
                return False
            return True
        return False
    except (ValueError, TypeError):
        return False

async def is_maintenance(user_id: int) -> bool:
    if await is_admin(user_id): return False
    data = await maintenance_collection.find_one({"_id": "maintenance"})
    return data is not None and data.get("maintenance") == "on"

async def get_auto_delete_status() -> bool:
    data = await settings_collection.find_one({"_id": "auto_delete"})
    return data.get("status", True) if data else True

async def set_auto_delete_status(status: bool):
    await settings_collection.update_one(
        {"_id": "auto_delete"}, 
        {"$set": {"status": status}}, 
        upsert=True
    )
    
