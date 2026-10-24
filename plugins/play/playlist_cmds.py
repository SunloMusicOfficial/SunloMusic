from pyrogram import Client, filters
from pyrogram.types import Message
from core.player import CURRENT_TRACK, add_to_queue
from database.mongodb import db
from utils.extractors import fetch_audio_url

@Client.on_message(filters.command("save") & filters.group)
async def save_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in CURRENT_TRACK:
        return await message.reply_text("❌ **Nothing is playing right now!**")
        
    track_data = CURRENT_TRACK[chat_id]
    result = await db.save_to_playlist(user_id, track_data)
    
    if result == "limit_reached":
        await message.reply_text("⚠️ **Playlist Full!** You can only save up to 50 songs.")
    elif result == "duplicate":
        await message.reply_text("⚠️ **Already Saved!** This song is already in your playlist.")
    else:
        await message.reply_text(f"✅ **Saved to your Cloud Playlist!**\n🎵 **{track_data['title']}**\n\nUse  to check.")

@Client.on_message(filters.command("myplaylist"))
async def myplaylist_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    playlist = user.get("playlist", [])
    
    if not playlist:
        return await message.reply_text("☁️ **Your Cloud Playlist is empty!**\nPlay a song and use  to add it here.")
        
    text = f"☁️ **{message.from_user.first_name}'s Cloud Playlist**\n\n"
    for i, song in enumerate(playlist, 1):
        text += f"**{i}.** {song['title']}\n"
        
    text += "\n▶️ Use  in a group to stream your entire playlist!"
    await message.reply_text(text)

@Client.on_message(filters.command("playall") & filters.group)
async def playall_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user = await db.get_user(user_id)
    playlist = user.get("playlist", [])
    
    if not playlist:
        return await message.reply_text("❌ You don't have any saved songs. Use  first.")
        
    status = await message.reply_text(f"🔄 **Loading {len(playlist)} songs from your Cloud...**")
    
    added_count = 0
    for song in playlist:
        # Pura gaana fetch na karke sirf queue me title insert karenge 
        # (Auto-play logic fetch karega jab baari aayegi)
        track_data = {"title": song["title"], "original_url": song["url"], "stream_url": None, "requested_by": user_id}
        add_to_queue(chat_id, track_data)
        added_count += 1
        
    await status.edit_text(f"✅ **{added_count} songs added to the Queue!**\nIf bot is not playing, use  to start your playlist.")
