from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    add_favorite, remove_favorite, get_favorites, is_favorite
)
from SunloMusic.queues import get_queue
from SunloMusic.formatters import format_duration

@bot.on_message(filters.command("like"))
@catch_errors
async def like_cmd(_, m: Message):
    # Works in group (uses current song) OR reply to any message with link
    q = get_queue(m.chat.id) if m.chat.type.name != "PRIVATE" else None
    
    if not q or not q.now_playing:
        return await m.reply_text(
            "❌ <b>Nothing is playing to like.</b>\n\n"
            "💡 <i>Tip: Reply to any song link with /like to save it!</i>"
        )
    
    np = q.now_playing
    if await is_favorite(m.from_user.id, np.url):
        return await m.reply_text("❤️ <b>Already in your favorites!</b>")
    
    await add_favorite(m.from_user.id, {
        "title": np.title,
        "url": np.url,
        "duration": np.duration,
        "thumbnail": np.thumbnail,
        "video": np.video,
    })
    
    await m.reply_text(
        f"❤️ <b>Added to favorites!</b>\n\n"
        f"🎵 {np.title}\n"
        f"━━━━━━━━━━━━━\n"
        f"View all: <code>/favorites</code>"
    )

@bot.on_message(filters.command("favorites"))
@catch_errors
async def favorites_cmd(_, m: Message):
    favs = await get_favorites(m.from_user.id, limit=30)
    if not favs:
        return await m.reply_text(
            "📭 <b>No favorites yet!</b>\n\n"
            "❤️ Use <code>/like</code> while a song is playing"
        )
    
    text = f"❤️ <b>Your Favorites ({len(favs)})</b>\n━━━━━━━━━━━━━\n"
    buttons = []
    for i, fav in enumerate(favs[:15], 1):
        dur = format_duration(fav.get("duration", 0))
        title = fav.get("title", "Unknown")[:40]
        text += f"{i}. {title} <i>({dur})</i>\n"
        buttons.append([InlineKeyboardButton(
            f"▶️ {title[:30]}",
            callback_data=f"favplay_{i-1}"
        )])
    
    buttons.append([InlineKeyboardButton("🗑 Clear All", callback_data="fav_clear")])
    await m.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_message(filters.command("playfav") & filters.group)
@catch_errors
async def playfav_cmd(_, m: Message):
    favs = await get_favorites(m.from_user.id, limit=50)
    if not favs:
        return await m.reply_text("📭 <b>No favorites to play.</b>\n\nFirst /like some songs!")
    
    q = get_queue(m.chat.id)
    from SunloMusic.queues import Track
    added = 0
    for fav in favs:
        track = Track(
            fav["title"], fav["url"], fav.get("duration", 0),
            fav.get("thumbnail", ""),
            m.from_user.first_name, m.from_user.id,
            fav.get("video", False)
        )
        if q.now_playing:
            q.queue.append(track)
        else:
            q.queue.append(track)
        added += 1
    
    await m.reply_text(
        f"✅ <b>Added {added} favorite songs to queue!</b>\n\n"
        f"Use <code>/play</code> with any song to start if not playing."
    )

@bot.on_callback_query(filters.regex("^favplay_"))
@catch_errors
async def fav_play_cb(_, cq: CallbackQuery):
    try: idx = int(cq.data.replace("favplay_", ""))
    except: return await cq.answer("Invalid", show_alert=True)
    
    favs = await get_favorites(cq.from_user.id, limit=30)
    if idx >= len(favs):
        return await cq.answer("Not found", show_alert=True)
    
    fav = favs[idx]
    await cq.answer(f"▶️ Sending /play...", show_alert=False)
    try:
        await cq.message.reply_text(f"/play {fav['url']}")
    except: pass

@bot.on_callback_query(filters.regex("^fav_clear$"))
@catch_errors
async def fav_clear_cb(_, cq: CallbackQuery):
    favs = await get_favorites(cq.from_user.id, limit=100)
    for fav in favs:
        await remove_favorite(cq.from_user.id, fav["url"])
    await cq.answer("🗑 All favorites cleared!", show_alert=True)
    try: await cq.message.delete()
    except: pass
