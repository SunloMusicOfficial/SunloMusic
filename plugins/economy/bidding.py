from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db
from core.player import bump_track, QUEUE

BUMP_COST = 100 # Queue me sabse aage aane ka price

@Client.on_message(filters.command("bump") & filters.group)
async def bump_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in QUEUE or len(QUEUE[chat_id]) < 2:
        return await message.reply_text("⚠️ **Queue is too short!**\nBump karne ke liye line me aur gaane hone chahiye.")
        
    user_data = await db.get_user(user_id)
    coins = user_data.get("coins", 0)
    
    if coins < BUMP_COST:
        return await message.reply_text(f"❌ **Not enough coins!**\nAapko {BUMP_COST} coins chahiye, par aapke paas sirf {coins} hain.\nUse  to get more.")
        
    # Coins katna
    await db.add_coins(user_id, -BUMP_COST)
    
    # Last added track ko aage lana
    last_track = QUEUE[chat_id].pop(-1)
    QUEUE[chat_id].insert(0, last_track)
    
    await message.reply_text(
        f"🚀 **VIP PRIORITY ACTIVATED!**\n\n"
        f"👤 {message.from_user.mention} paid **{BUMP_COST} Coins** to bump their song!\n"
        f"🎵 **{last_track['title']}** is now **Next in Queue (#1)**."
    )
