import asyncio, time, base64, hashlib, os, random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LinkPreviewOptions
from SunloMusic.bot import bot, ensure_assistant_in_chat
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import _search_ytdlp_multi_sync, extract_audio, download_media_file, cleanup_download
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER
from SunloMusic.queues import get_queue, Track, KARAOKE_CHATS
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.thumbnails import generate_thumbnail, get_default_thumb
from SunloMusic.keyboards import player_keyboard
from SunloMusic.database import add_recent
from SunloMusic.lyrics import start_live_karaoke

CATEGORIES = {
    "hindi": "trending hindi songs 2024",
    "punjabi": "top punjabi hits 2024",
    "english": "top english hits 2024",
    "lofi": "lofi hindi songs",
    "arijit": "arijit singh best songs",
    "old": "old hindi classic songs",
}

TRENDING_CACHE = {}
LOADING_EMOJIS = ["✨", "🌸", "🪄", "🌟", "🦋", "🎧", "🎶", "🍃", "🔥", "💫", "🪐", "🌈"]

@bot.on_message(filters.command("trending"))
@catch_errors
async def trending_cmd(_, m: Message):
    buttons = [
        [InlineKeyboardButton("🎬 Bollywood", callback_data="tr_hindi"),
         InlineKeyboardButton("🎤 Punjabi", callback_data="tr_punjabi")],
        [InlineKeyboardButton("🌍 English", callback_data="tr_english"),
         InlineKeyboardButton("🌙 Lo-Fi", callback_data="tr_lofi")],
        [InlineKeyboardButton("🎼 Arijit", callback_data="tr_arijit"),
         InlineKeyboardButton("📻 Old Classics", callback_data="tr_old")],
    ]
    await m.reply_text(
        "<b>🔥 Trending Charts</b>\n━━━━━━━━━━━━━\n"
        "Choose a category to see top songs:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex(r"^tr_(hindi|punjabi|english|lofi|arijit|old)$"))
@catch_errors
async def trending_category(_, cq: CallbackQuery):
    cat = cq.data.replace("tr_", "")
    
    await cq.answer(f"🔍 Loading {cat}...")
    try: await cq.message.edit_text(f"{random.choice(LOADING_EMOJIS)} <b>Fetching {cat} top songs...</b>")
    except: pass
    
    loop = asyncio.get_running_loop()
    try:
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _search_ytdlp_multi_sync, CATEGORIES[cat], 10),
            timeout=15.0
        )
    except:
        results = []
    
    if not results:
        return await cq.message.edit_text("❌ <b>Could not fetch trending songs.</b>")
    
    TRENDING_CACHE.clear()
    
    text = f"<b>🔥 Trending: {cat.title()}</b>\n━━━━━━━━━━━━━\n\n"
    buttons = []
    for i, r in enumerate(results, 1):
        dur = format_duration(r.get("duration", 0))
        title = r.get("title", "Unknown")[:45]
        text += f"{i}. {title} <i>({dur})</i>\n"
        
        cache_key = hashlib.md5(r['url'].encode()).hexdigest()[:8]
        TRENDING_CACHE[cache_key] = r
        
        buttons.append([InlineKeyboardButton(
            f"▶️ {title[:35]}",
            callback_data=f"trplay_{cache_key}"
        )])
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="tr_back")])
    
    await cq.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons[:10] + [[InlineKeyboardButton("🔙 Back", callback_data="tr_back")]])
    )

@bot.on_callback_query(filters.regex("^tr_back$"))
@catch_errors
async def tr_back(_, cq: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("🎬 Bollywood", callback_data="tr_hindi"),
         InlineKeyboardButton("🎤 Punjabi", callback_data="tr_punjabi")],
        [InlineKeyboardButton("🌍 English", callback_data="tr_english"),
         InlineKeyboardButton("🌙 Lo-Fi", callback_data="tr_lofi")],
        [InlineKeyboardButton("🎼 Arijit", callback_data="tr_arijit"),
         InlineKeyboardButton("📻 Old Classics", callback_data="tr_old")],
    ]
    await cq.message.edit_text(
        "<b>🔥 Trending Charts</b>\n━━━━━━━━━━━━━\n"
        "Choose a category to see top songs:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex("^trplay_"))
@catch_errors
async def tr_play(_, cq: CallbackQuery):
    cache_key = cq.data.replace("trplay_", "")
    r = TRENDING_CACHE.get(cache_key)
    if not r:
        return await cq.answer("Session expired. Please /trending again.", show_alert=True)
        
    await cq.answer("⏳ Loading Details...")
    
    thumb = r.get("thumbnail")
    title = r.get("title", "Unknown")
    dur = r.get("duration", 0)
    
    caption = (
        f"<b>🎵 Song Details</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎶 <b>Title:</b> {title}\n"
        f"⏱ <b>Duration:</b> {format_duration(dur)}\n"
        f"👤 <b>Requester:</b> {cq.from_user.mention}\n"
        f"━━━━━━━━━━━━━\n"
        f"👇 <b>Choose an action below:</b>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Play in VC", callback_data=f"tr_act_play_{cache_key}"),
         InlineKeyboardButton("📥 Download", callback_data=f"tr_act_dl_{cache_key}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="tr_act_cancel")]
    ])
    
    try:
        if thumb:
            await cq.message.reply_photo(thumb, caption=caption, reply_markup=buttons)
        else:
            await cq.message.reply_text(caption, reply_markup=buttons, link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception as e:
        LOGGER.error(f"Preview photo error: {e}")
        await cq.message.reply_text(caption, reply_markup=buttons, link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex("^tr_act_cancel$"))
@catch_errors
async def tr_cancel(_, cq: CallbackQuery):
    await cq.message.delete()
    await cq.answer("Cancelled.")

@bot.on_callback_query(filters.regex("^tr_act_play_"))
@catch_errors
async def tr_act_play(_, cq: CallbackQuery):
    cache_key = cq.data.replace("tr_act_play_", "")
    r = TRENDING_CACHE.get(cache_key)
    if not r:
        return await cq.answer("Session expired.", show_alert=True)
    url = r["url"]
    
    await cq.answer("⚡ Loading into VC...")
    status = await cq.message.reply_text(f"{random.choice(LOADING_EMOJIS)} <b>Loading your music...</b>")
    
    if not await ensure_assistant_in_chat(cq.message.chat.id):
        return await status.edit_text("❌ <b>Assistant could not join the group!</b>")
        
    info = await extract_audio(url)
    if not info:
        return await status.edit_text("❌ <b>Failed to fetch media.</b>")
    
    title = info.get("title", "Unknown")
    dur = info.get("duration", 0)
    thumb = info.get("thumbnail", "")
    
    if title in ["Unknown", "Direct Link"] and r.get("title"): title = r["title"]
    if dur == 0 and r.get("duration"): dur = r["duration"]
    if not thumb and r.get("thumbnail"): thumb = r["thumbnail"]
        
    safe_title = title[:40] + "..." if len(title) > 40 else title
    
    q = get_queue(cq.message.chat.id)
    track = Track(safe_title, info["url"], dur, thumb, cq.from_user.first_name, cq.from_user.id, False)
    
    if q.now_playing:
        q.queue.append(track)
        await status.delete()
        try: await cq.message.delete()
        except: pass
        
        thumb_img = await generate_thumbnail(cq.message.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
        b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        caption = f"<b>📥 Added to Queue 📥</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{track.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n━━━━━━━━━━━━━\n📌 Position: {len(q.queue)}\n━━━━━━━━━━━━━"
        
        sent_msg = None
        if thumb_img:
            try: sent_msg = await cq.message.reply_photo(thumb_img, caption=caption)
            except: pass
        if not sent_msg:
            sent_msg = await cq.message.reply_text(caption, link_preview_options=LinkPreviewOptions(is_disabled=True))
        return
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    
    await status.delete()
    try: await cq.message.delete()
    except: pass
    
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
    thumb_img = await generate_thumbnail(cq.message.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
    caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{track.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n━━━━━━━━━━━━━"
    
    # ✅ ULTRA FAST: Send Card and Join VC at the EXACT same time!
    async def send_card():
        if thumb_img:
            try: return await cq.message.reply_photo(thumb_img, caption=caption, reply_markup=player_keyboard(q, 0))
            except: pass
        local_thumb = get_default_thumb()
        if local_thumb:
            try: return await cq.message.reply_photo(local_thumb, caption=caption, reply_markup=player_keyboard(q, 0))
            except: pass
        return await cq.message.reply_text(caption, reply_markup=player_keyboard(q, 0), link_preview_options=LinkPreviewOptions(is_disabled=True))
    
    sent_msg, _ = await asyncio.gather(send_card(), play_stream(cq.message.chat.id, track.url, track.video))
    
    q.playing_message_id = sent_msg.id
    try: await sent_msg.pin(disable_notification=True)
    except: pass
    
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(cq.message.chat.id, sent_msg.id))
    
    if cq.message.chat.id in KARAOKE_CHATS:
        q.karaoke_task = asyncio.create_task(start_live_karaoke(bot, cq.message.chat.id, track.title, track.duration, q))
    
    asyncio.create_task(add_recent(cq.message.chat.id, {
        "title": track.title, "url": track.url,
        "duration": track.duration, "thumbnail": track.thumbnail,
        "requester": track.requester, "requester_id": track.requester_id,
        "video": track.video
    }))

@bot.on_callback_query(filters.regex("^tr_act_dl_"))
@catch_errors
async def tr_act_dl(_, cq: CallbackQuery):
    cache_key = cq.data.replace("tr_act_dl_", "")
    r = TRENDING_CACHE.get(cache_key)
    if not r:
        return await cq.answer("Session expired.", show_alert=True)
    url = r["url"]
    
    await cq.answer("⬇️ Downloading Audio...")
    status = await cq.message.reply_text(f"{random.choice(LOADING_EMOJIS)} <b>Downloading audio, please wait...</b>\n<i>(This may take a minute)</i>")
    
    result = await download_media_file(url, video=False)
    if not result or not result.get("path") or not os.path.exists(result["path"]):
        return await status.edit_text("❌ <b>Download failed.</b>")
        
    try:
        await status.edit_text(f"{random.choice(LOADING_EMOJIS)} <b>Uploading to Telegram...</b>")
        await cq.message.reply_audio(
            audio=result["path"],
            title=result.get("title", r.get("title", "Unknown"))[:64],
            performer="SunloMusic",
            duration=result.get("duration", r.get("duration", 0)),
            caption=f"🎵 <b>{result.get('title', r.get('title', 'Unknown'))}</b>\n\n🤖 Downloaded via @{config.BOT_USERNAME.strip('@')}"
        )
        await status.delete()
        try: await cq.message.delete()
        except: pass
    except Exception as e:
        LOGGER.error(f"Upload error: {e}")
        await status.edit_text("❌ <b>Upload failed.</b>")
    finally:
        cleanup_download(result["path"])
