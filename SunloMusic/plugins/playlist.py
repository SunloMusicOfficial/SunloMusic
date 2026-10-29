from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.database import save_gplaylist, get_gplaylist
from SunloMusic.queues import get_queue, Track

@bot.on_message(filters.command("gsave") & filters.group)
@catch_errors
@admin_only
async def gsave_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/gsave party</code>")
    
    name = m.command[1].lower()
    q = get_queue(m.chat.id)
    
    if not q.now_playing and not q.queue:
        return await m.reply_text("❌ <b>Queue is empty, nothing to save.</b>")
        
    queue_data = []
    if q.now_playing:
        queue_data.append({"title": q.now_playing.title, "url": q.now_playing.url, "duration": q.now_playing.duration, "thumbnail": q.now_playing.thumbnail, "requester": "Playlist", "requester_id": 0})
    for t in q.queue:
        queue_data.append({"title": t.title, "url": t.url, "duration": t.duration, "thumbnail": t.thumbnail, "requester": "Playlist", "requester_id": 0})
        
    await save_gplaylist(m.chat.id, name, queue_data)
    await m.reply_text(f"✅ <b>Group Playlist saved as '{name}'!</b>\nLoad it anytime using <code>/gload {name}</code>.")

@bot.on_message(filters.command("gload") & filters.group)
@catch_errors
@admin_only
async def gload_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/gload party</code>")
        
    name = m.command[1].lower()
    data = await get_gplaylist(m.chat.id, name)
    
    if not data:
        return await m.reply_text(f"❌ <b>No group playlist found with name '{name}'.</b>")
        
    q = get_queue(m.chat.id)
    for item in data:
        track = Track(item["title"], item["url"], item["duration"], item["thumbnail"], m.from_user.first_name, m.from_user.id, False)
        q.queue.append(track)
        
    await m.reply_text(f"✅ <b>Group Playlist '{name}' loaded with {len(data)} tracks!</b>")
