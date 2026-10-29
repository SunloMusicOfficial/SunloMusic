from motor.motor_asyncio import AsyncIOMotorClient
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

client = AsyncIOMotorClient(config.MONGO_URL)
db = client["SunloMusic"]
users_col = db["users"]
chats_col = db["chats"]
sudo_col = db["sudoers"]
playlists_col = db["playlists"]
thumbs_col = db["thumbs"]
lb_col = db["leaderboard"]
gplaylists_col = db["gplaylists"]
afk_col = db["afk"]
settings_col = db["settings"]

SPAM_DICT = {}

async def add_user(user_id: int, name: str = ""):
    await users_col.update_one({"user_id": user_id}, {"$setOnInsert": {"user_id": user_id, "name": name}}, upsert=True)

async def is_sudo(user_id: int) -> bool:
    if user_id in config.sudo_list or user_id == config.OWNER_ID: return True
    return await sudo_col.find_one({"user_id": user_id}) is not None

async def add_sudo(user_id: int):
    await sudo_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_sudo(user_id: int):
    await sudo_col.delete_one({"user_id": user_id})

async def get_chat(chat_id: int) -> dict:
    return await chats_col.find_one({"chat_id": chat_id}) or {"chat_id": chat_id, "auth": False}

async def set_auth(chat_id: int, status: bool):
    await chats_col.update_one({"chat_id": chat_id}, {"$set": {"auth": status}}, upsert=True)

async def get_stats() -> dict:
    return {"users": await users_col.count_documents({}), "chats": await chats_col.count_documents({})}

async def get_all_chats() -> list:
    return [c["chat_id"] async for c in chats_col.find({}, {"chat_id": 1})]

# ✅ Thumbnails (Wapas add kiye gaye)
async def set_custom_thumb(chat_id: int, file_id: str):
    await thumbs_col.update_one({"chat_id": chat_id}, {"$set": {"file_id": file_id}}, upsert=True)

async def get_custom_thumb(chat_id: int) -> str:
    data = await thumbs_col.find_one({"chat_id": chat_id})
    return data["file_id"] if data else None

async def del_custom_thumb(chat_id: int):
    await thumbs_col.delete_one({"chat_id": chat_id})

# Group Settings
async def set_group_setting(chat_id: int, key: str, value: any):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

async def get_group_setting(chat_id: int, key: str, default: any = None):
    data = await settings_col.find_one({"chat_id": chat_id})
    return data.get(key, default) if data else default

# Leaderboard
async def add_lb_point(chat_id: int, user_id: int, user_name: str):
    await lb_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"points": 1}, "$set": {"name": user_name}},
        upsert=True
    )

async def get_leaderboard(chat_id: int, limit: int = 5):
    return await lb_col.find({"chat_id": chat_id}).sort("points", -1).limit(limit).to_list(limit)

# Group Playlists
async def save_gplaylist(chat_id: int, name: str, queue_data: list):
    await gplaylists_col.update_one(
        {"chat_id": chat_id, "name": name},
        {"$set": {"queue": queue_data}},
        upsert=True
    )

async def get_gplaylist(chat_id: int, name: str):
    data = await gplaylists_col.find_one({"chat_id": chat_id, "name": name})
    return data["queue"] if data else None

# AFK
async def set_afk(user_id: int, reason: str):
    await afk_col.update_one({"user_id": user_id}, {"$set": {"reason": reason}}, upsert=True)

async def get_afk(user_id: int):
    data = await afk_col.find_one({"user_id": user_id})
    return data["reason"] if data else None

async def remove_afk(user_id: int):
    await afk_col.delete_one({"user_id": user_id})
