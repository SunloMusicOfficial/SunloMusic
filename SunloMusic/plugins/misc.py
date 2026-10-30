import time
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import get_recent, add_recent
from SunloMusic.queues import get_queue, Track
from SunloMusic.calls import play_stream
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration

@bot.on_message(filters.command("recent") & filters.group)
@catch_errors
async def recent_cmd(_, m: Message):
    tracks = await get_recent(m.chat.id)
    if not tracks:
        return await m.reply_text("📭 <b>No recent songs in this chat.</b>")
    
    text = f"<b>🕒 Recently Played ({len(tracks)})</b>\n━━━━━━━━━━━━━\n"
    for i, t in enumerate(reversed(tracks[-10:]), 1):
        dur = format_duration(t.get("duration", 0))
        text += f"{i}. {t['title'][:40]} <i>({dur})</i>\n"
    
    await m.reply_text(text)

@bot.on_message(filters.command("dedicate") & filters.group)
@catch_errors
async def dedicate_cmd(_, m: Message):
    if len(m.command) < 3:
        return await m.reply_text(
            "❌ <b>Usage:</b> <code>/dedicate @user song name</code>\n\n"
            "Example: <code>/dedicate @sakil tum hi ho</code>"
        )
    
    # Parse target and song
    target = None
    song_parts = []
    for part in m.command[1:]:
        if part.startswith("@") and target is None:
            target = part
        else:
            song_parts.append(part)
    
    if not target:
        return await m.reply_text("❌ <b>Mention a user to dedicate to!</b>")
    
    song = " ".join(song_parts)
    if not song:
        return await m.reply_text("❌ <b>Give a song name too.</b>")
    
    status = await m.reply_text(f"💝 Preparing dedication...")
    
    info = await extract_audio(song)
    if not info:
        return await status.edit_text("❌ <b>Song not found.</b>")
    
    q = get_queue(m.chat.id)
    track = Track(
        info["title"], info["url"], info["duration"],
        info["thumbnail"], m.from_user.first_name, m.from_user.id, False
    )
    
    # Send dedication message
    ded_text = (
        f"💝 <b>Song Dedication</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎵 <b>{info['title']}</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"📤 <b>From:</b> <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>\n"
        f"📥 <b>To:</b> {target}\n"
        f"━━━━━━━━━━━━━\n"
        f"<i>{'Queued!' if q.now_playing else 'Starting now...'}</i>"
    )
    
    if q.now_playing:
        q.queue.append(track)
        await status.edit_text(ded_text)
    else:
        await play_stream(m.chat.id, track.url, track.video)
        q.now_playing = track
        q.start_time = time.time()
        q.total_paused = 0
        q.paused = False
        q.votes = set()
        
        try:
            await add_recent(m.chat.id, {
                "title": track.title, "url": track.url,
                "duration": track.duration, "thumbnail": track.thumbnail,
                "requester": track.requester, "requester_id": track.requester_id,
                "video": track.video
            })
        except: pass
        
        await status.edit_text(ded_text)
