from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db

@Client.on_message(filters.command(["leaderboard", "top"]))
async def leaderboard_cmd(client: Client, message: Message):
    status = await message.reply_text("🏆 **Fetching Global Hall of Fame...**")
    
    top_users = await db.get_top_users()
    if not top_users:
        return await status.edit_text("❌ No data available yet.")
        
    text = "🏆 **SunloMusic - Global Hall of Fame** 🏆\n\n"
    text += "🎵 **Top Music Listeners:**\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        plays = user.get("play_count", 0)
        
        try:
            # Username fetch karne ka try karega
            tg_user = await client.get_users(user["user_id"])
            name = tg_user.first_name
        except:
            name = f"User {user['user_id']}"
            
        text += f"{medal} **{name}** ━ `{plays} Plays`\n"
        
    text += "\n💡 *Play more songs to rank up on the global leaderboard!*"
    await status.edit_text(text)
