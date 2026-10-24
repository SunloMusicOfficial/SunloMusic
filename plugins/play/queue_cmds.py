from pyrogram import Client, filters
from pyrogram.types import Message
from core.player import QUEUE, CURRENT_TRACK

@Client.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in CURRENT_TRACK and (chat_id not in QUEUE or not QUEUE[chat_id]):
        return await message.reply_text("📭 **Queue is completely empty!**")
        
    text = "📋 **Current Queue List**\n\n"
    
    if chat_id in CURRENT_TRACK:
        text += f"▶️ **Now Playing:** {CURRENT_TRACK[chat_id]['title']}\n\n"
        
    if chat_id in QUEUE and QUEUE[chat_id]:
        text += "⏳ **Up Next:**\n"
        for i, track in enumerate(QUEUE[chat_id][:10], 1): # Show max 10 songs
            text += f"**{i}.** {track['title']}\n"
            
        if len(QUEUE[chat_id]) > 10:
            text += f"\n*...and {len(QUEUE[chat_id]) - 10} more tracks.*"
            
    await message.reply_text(text)
