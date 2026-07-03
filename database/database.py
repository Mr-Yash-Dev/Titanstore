import motor.motor_asyncio
from datetime import datetime, timedelta
from config import DB_URI, DB_NAME, OWNER_ID

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
telegram_files = database["telegram_files"]
premium_collection = database["premium_users"]

# -------------------------------
# USER MANAGEMENT
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def add_user(user_id: int, first_name=None, username=None):
    await user_data.update_one(
        {"_id": user_id},
        {"$set": {"first_name": first_name, "username": username, "joined_at": datetime.now()}},
        upsert=True
    )

async def get_all_users():
    cursor = user_data.find({}, {"_id": 1})
    users = await cursor.to_list(length=None)
    return [user["_id"] for user in users]

async def delete_user(user_id: int):
    await user_data.delete_one({"_id": user_id})

# -------------------------------
# BAN SYSTEM
# -------------------------------
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

# -------------------------------
# ADMIN SYSTEM
# -------------------------------
async def add_admin(user_id: int):
    await admins_collection.update_one({"_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)

async def remove_admin(user_id: int):
    await admins_collection.delete_one({"_id": user_id})

async def get_admins():
    cursor = admins_collection.find({}, {"_id": 1})
    admins = await cursor.to_list(length=None)
    return [admin["_id"] for admin in admins]

async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID: return True
    data = await admins_collection.find_one({"_id": user_id})
    return data is not None and data.get("is_admin", False)

# -------------------------------
# PREMIUM SYSTEM
# -------------------------------
async def add_premium(user_id: int, days: int):
    expires_at = datetime.now() + timedelta(days=days)
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
    if await is_admin(user_id): return True # Admins/Owners inherently get premium rights
    
    data = await premium_collection.find_one({"_id": user_id})
    if data and data.get("is_premium"):
        expires_at = data.get("expires_at")
        if expires_at and datetime.now() > expires_at:
            await remove_premium(user_id)
            return False
        return True
    return False

# -------------------------------
# MAINTENANCE SYSTEM
# -------------------------------
async def is_maintenance(user_id: int) -> bool:
    if user_id == OWNER_ID: return False
    data = await maintenance_collection.find_one({"_id": "maintenance"})
    return data is not None and data.get("maintenance") == "on"
    
