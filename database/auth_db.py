from database.mongodb import db

async def get_sudo_users():
    if not db.client: return []
    data = await db.db.config.find_one({"_id": "sudo_users"})
    return data.get("users", []) if data else []

async def add_sudo(user_id: int):
    sudo_users = await get_sudo_users()
    if user_id not in sudo_users:
        sudo_users.append(user_id)
        await db.db.config.update_one({"_id": "sudo_users"}, {"$set": {"users": sudo_users}}, upsert=True)

async def is_auth(chat_id: int, user_id: int):
    group = await db.get_group(chat_id)
    auth_users = group.get("auth_users", [])
    return user_id in auth_users
