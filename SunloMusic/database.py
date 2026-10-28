from motor.motor_asyncio import AsyncIOMotorClient
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

client = AsyncIOMotorClient(config.MONGO_URL)
db = client["SunloMusic"]
users_col = db["users"]
chats_col = db["chats"]
sudo_col = db["sudoers"]
playlists_col = db["playlists"]

# ✅ In-Memory Spam Control
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

async def save_playlist(user_id: int, name: str, queue_data: list):
    await playlists_col.update_one(
        {"user_id": user_id, "name": name},
        {"$set": {"queue": queue_data}},
        upsert=True
    )

async def get_playlist(user_id: int, name: str) -> list:
    data = await playlists_col.find_one({"user_id": user_id, "name": name})
    return data["queue"] if data else None

LOGGER.info("✅ MongoDB connected successfully")
