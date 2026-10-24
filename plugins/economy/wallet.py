from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db

@Client.on_message(filters.command(["wallet", "coins"]))
async def wallet_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await db.get_user(user_id)
    coins = user_data.get("coins", 0)
    
    await message.reply_text(
        f"💳 **SunloMusic Wallet**\n\n"
        f"👤 **User:** {message.from_user.mention}\n"
        f"🪙 **Balance:** `{coins}` Sunlo Coins\n\n"
        f"💡 *Tip: Use /daily to get free coins, and /bump to skip the queue!*"
    )

@Client.on_message(filters.command("daily"))
async def daily_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Simple logic: Har bar command dene par 50 coins (Future me cooldown add kar sakte hain)
    new_balance = await db.add_coins(user_id, 50)
    
    await message.reply_text(
        f"🎉 **Daily Reward Claimed!**\n"
        f"Aapko **50 Sunlo Coins** mil gaye hain.\n"
        f"🪙 **New Balance:** `{new_balance}` Coins"
    )
