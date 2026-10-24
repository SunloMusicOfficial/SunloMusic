import random
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db

@Client.on_message(filters.command("match"))
async def match_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke  type karein.")
        
    user1 = message.from_user
    user2 = message.reply_to_message.from_user
    
    if user1.id == user2.id:
        return await message.reply_text("❌ Khud se match nahi kar sakte!")
        
    # Generate a realistic-looking compatibility score
    score = random.randint(40, 99)
    
    vibe = "Soulmates 🔥" if score > 85 else "Good Vibes 🎵" if score > 70 else "Different Tastes 🤔"
    
    await message.reply_text(
        f"🎧 **Music Compatibility Test** 🎧\n\n"
        f"👤 {user1.first_name} ✖️ {user2.first_name}\n"
        f"📊 **Match Score:** `{score}%`\n"
        f"💡 **Vibe:** {vibe}"
    )
