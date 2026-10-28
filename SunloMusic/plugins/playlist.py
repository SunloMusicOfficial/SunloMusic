from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import save_playlist, get_playlist
from SunloMusic.queues import get_queue, Track

@bot.on_message(filters.command("save") & filters.group)
@catch_errors
async def save_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/save party</code>")
    
    name = m.command[1].lower()
    q = get_queue(m.chat.id)
    
    if not q.now_playing and not q.queue:
        return await m.reply_text("❌ <b>Queue is empty, nothing to save.</b>")
        
    queue_data = []
    if q.now_playing:
        queue_data.append({"title": q.now_playing.title, "url": q.now_playing.url, "duration": q.now_playing.duration, "thumbnail": q.now_playing.thumbnail, "requester": "Playlist", "requester_id": 0})
    for t in q.queue:
        queue_data.append({"title": t.title, "url": t.url, "duration": t.duration, "thumbnail": t.thumbnail, "requester": "Playlist", "requester_id": 0})
        
    await save_playlist(m.from_user.id, name, queue_data)
    await m.reply_text(f"✅ <b>Playlist saved as '{name}'!</b>\nYou can load it anytime using <code>/load {name}</code>.")

@bot.on_message(filters.command("load") & filters.group)
@catch_errors
async def load_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/load party</code>")
        
    name = m.command[1].lower()
    data = await get_playlist(m.from_user.id, name)
    
    if not data:
        return await m.reply_text(f"❌ <b>No playlist found with name '{name}'.</b>")
        
    q = get_queue(m.chat.id)
    for item in data:
        track = Track(item["title"], item["url"], item["duration"], item["thumbnail"], m.from_user.first_name, m.from_user.id, False)
        q.queue.append(track)
        
    await m.reply_text(f"✅ <b>Playlist '{name}' loaded with {len(data)} tracks!</b>\nUse <code>/skip</code> or <code>/play</code> to start.")
