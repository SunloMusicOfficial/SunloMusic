from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    save_playlist, get_playlist, get_all_user_playlists,
    delete_user_playlist
)
from SunloMusic.queues import get_queue, Track, active_chats
from SunloMusic.formatters import format_duration

# ✅ Removed filters.private so it works in Groups too
@bot.on_message(filters.command("save"))
@catch_errors
async def save_personal(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text(
            "❌ <b>Usage:</b> <code>/save playlist_name</code>\n\n"
            "<i>⚠️ This saves songs from active group queues to your personal playlist.\n"
            "Or use <code>/addsong playlist_name song name</code> to add by search.</i>"
        )
    
    name = m.command[1].lower()
    user_id = m.from_user.id
    queue_data = []
    
    # Get songs from active queues
    for chat_id in active_chats():
        q = get_queue(chat_id)
        if q.now_playing:
            queue_data.append({
                "title": q.now_playing.title,
                "url": q.now_playing.url,
                "duration": q.now_playing.duration,
                "thumbnail": q.now_playing.thumbnail,
                "requester": q.now_playing.requester,
                "requester_id": q.now_playing.requester_id,
                "video": q.now_playing.video,
            })
    
    if not queue_data:
        return await m.reply_text("📭 <b>No active music found to save.</b>\nUse /addsong to add songs manually.")
    
    await save_playlist(user_id, name, queue_data)
    await m.reply_text(f"✅ <b>Playlist '{name}' saved with {len(queue_data)} tracks!</b>\n\nPlay with <code>/load {name}</code>")

@bot.on_message(filters.command("addsong"))
@catch_errors
async def addsong_cmd(_, m: Message):
    if len(m.command) < 3:
        return await m.reply_text("❌ <b>Usage:</b> <code>/addsong playlist_name song name</code>")
    
    name = m.command[1].lower()
    song_query = " ".join(m.command[2:])
    user_id = m.from_user.id
    
    status = await m.reply_text(f"🔍 <b>Searching:</b> {song_query}...")
    
    from SunloMusic.ytdlp import extract_audio
    info = await extract_audio(song_query)
    if not info:
        return await status.edit_text("❌ <b>Song not found.</b>")
    
    existing = await get_playlist(user_id, name) or []
    existing.append({
        "title": info["title"],
        "url": info["url"],
        "duration": info["duration"],
        "thumbnail": info["thumbnail"],
        "requester": m.from_user.first_name,
        "requester_id": user_id,
        "video": False,
    })
    
    await save_playlist(user_id, name, existing)
    await status.edit_text(
        f"✅ <b>Added:</b> {info['title'][:60]}\n"
        f"📀 <b>Playlist:</b> {name} ({len(existing)} tracks)"
    )

@bot.on_message(filters.command("myplaylists"))
@catch_errors
async def myplaylists_cmd(_, m: Message):
    user_id = m.from_user.id
    playlists = await get_all_user_playlists(user_id)
    
    if not playlists:
        return await m.reply_text(
            "📭 <b>No playlists yet.</b>\n\n"
            "Create one with:\n"
            "<code>/addsong myfav song name</code>"
        )
    
    text = f"<b>📀 {m.from_user.first_name}'s Playlists</b>\n━━━━━━━━━━━━━\n"
    buttons = []
    for p in playlists[:15]:
        text += f"🎵 <b>{p['name']}</b> — {p['count']} tracks\n"
        buttons.append([InlineKeyboardButton(
            f"▶️ {p['name']} ({p['count']})",
            callback_data=f"plplay_{user_id}_{p['name']}"
        )])
    
    await m.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons[:10]))

@bot.on_message(filters.command("load"))
@catch_errors
async def load_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/load playlist_name</code>\n\n<i>Must be in a group VC to use this</i>")
    
    name = m.command[1].lower()
    user_id = m.from_user.id
    
    data = await get_playlist(user_id, name)
    if not data:
        return await m.reply_text(f"❌ <b>Playlist '{name}' not found.</b>")
    
    if m.chat.type.name == "PRIVATE":
        return await m.reply_text(
            f"✅ <b>Playlist '{name}' loaded:</b> {len(data)} tracks\n\n"
            f"⚠️ <b>To play in VC:</b> Use <code>/load {name}</code> in a group."
        )
        
    # If in group, load and play
    q = get_queue(m.chat.id)
    for item in data:
        track = Track(item["title"], item["url"], item["duration"], item["thumbnail"], m.from_user.first_name, m.from_user.id, item.get("video", False))
        q.queue.append(track)
    
    await m.reply_text(f"✅ <b>Playlist '{name}' added to queue with {len(data)} tracks!</b>\n\nUse <code>/play</code> to start playing if not playing.")

@bot.on_message(filters.command("delplaylist"))
@catch_errors
async def delplaylist_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/delplaylist playlist_name</code>")
    
    name = m.command[1].lower()
    await delete_user_playlist(m.from_user.id, name)
    await m.reply_text(f"🗑 <b>Playlist '{name}' deleted.</b>")

@bot.on_callback_query(filters.regex("^plplay_"))
@catch_errors
async def plplay_cb(_, cq):
    parts = cq.data.split("_", 2)
    if len(parts) < 3: return await cq.answer("Invalid", show_alert=True)
    _, owner_id, name = parts
    if cq.from_user.id != int(owner_id):
        return await cq.answer("This is not your playlist!", show_alert=True)
    
    data = await get_playlist(int(owner_id), name)
    if not data:
        return await cq.answer("Playlist not found", show_alert=True)
    
    text = f"<b>📀 Playlist: {name}</b>\n━━━━━━━━━━━━━\n"
    for i, t in enumerate(data[:10], 1):
        text += f"{i}. {t['title'][:40]}\n"
    
    await cq.answer("✅", show_alert=False)
    try: await cq.message.edit_text(text)
    except: pass
