import asyncio, random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import extract_audio
from SunloMusic.calls import play_stream
from SunloMusic.queues import get_queue, Track
from SunloMusic.database import add_recent

active_battles = {}

@bot.on_message(filters.command("battle") & filters.group)
@catch_errors
async def battle_cmd(_, m: Message):
    if len(m.command) < 2 or "vs" not in m.text.lower():
        return await m.reply_text("❌ <b>Usage:</b> <code>/battle song1 vs song2</code>\nExample: <code>/battle Kesariya vs Tum Hi Ho</code>")
    
    # Parse songs
    query = m.text.split(None, 1)[1]
    parts = query.lower().split(" vs ")
    if len(parts) != 2:
        return await m.reply_text("❌ <b>Use 'vs' to separate songs.</b>")
    
    song1, song2 = parts[0].strip(), parts[1].strip()
    status = await m.reply_text("⚔️ <b>Preparing Battle...</b>\nFetching both tracks...")
    
    info1 = await extract_audio(song1)
    info2 = await extract_audio(song2)
    
    if not info1 or not info2:
        return await status.edit_text("❌ <b>Could not find one or both songs.</b>")
    
    active_battles[m.chat.id] = {
        "song1": info1, "song2": info2,
        "votes1": 0, "votes2": 0,
        "voters": set()
    }
    
    text = (
        "⚔️ <b>MUSIC BATTLE!</b> ⚔️\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🅰️ <b>{info1['title'][:30]}</b>\n"
        "🆚\n"
        f"🅱️ <b>{info2['title'][:30]}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👇 <b>Vote for your favorite!</b>\n"
        "<i>(Song snippets will play alternately)</i>"
    )
    
    await status.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🅰️ Vote {info1['title'][:15]}", callback_data="vote_1"), InlineKeyboardButton(f"🅱️ Vote {info2['title'][:15]}", callback_data="vote_2")]
    ]))
    
    # Play 15 seconds of Song 1
    await play_stream(m.chat.id, info1["url"], False, seek_time=0)
    await asyncio.sleep(15)
    
    # Play 15 seconds of Song 2
    await play_stream(m.chat.id, info2["url"], False, seek_time=0)
    await asyncio.sleep(15)
    
    # End battle
    try:
        await status.delete()
    except: pass
    
    if m.chat.id in active_battles:
        data = active_battles.pop(m.chat.id)
        v1, v2 = data["votes1"], data["votes2"]
        winner = info1 if v1 > v2 else info2 if v2 > v1 else None
        
        if winner:
            await m.reply_text(f"🏆 <b>WINNER:</b> {winner['title']}\nWith {max(v1, v2)} votes!")
            # Play the full winner song
            track = Track(winner["title"], winner["url"], winner["duration"], winner["thumbnail"], m.from_user.first_name, m.from_user.id, False)
            q = get_queue(m.chat.id)
            q.now_playing = track
            q.start_time = asyncio.get_event_loop().time()
            await play_stream(m.chat.id, track.url, False)
        else:
            await m.reply_text("🤝 <b>It's a TIE!</b> No winner.")

@bot.on_callback_query(filters.regex(r"^vote_(1|2)$"))
@catch_errors
async def vote_cb(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    if chat_id not in active_battles:
        return await cq.answer("Battle has ended!", show_alert=True)
    
    data = active_battles[chat_id]
    if cq.from_user.id in data["voters"]:
        return await cq.answer("You already voted!", show_alert=True)
    
    choice = cq.data.split("_")[1]
    if choice == "1": data["votes1"] += 1
    else: data["votes2"] += 1
    
    data["voters"].add(cq.from_user.id)
    await cq.answer("✅ Vote counted!")
