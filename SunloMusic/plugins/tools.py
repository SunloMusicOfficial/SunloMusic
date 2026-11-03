import asyncio
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS, AUTO_DJ_CHATS, TTS_CHATS, VOICE_CMD_CHATS, get_queue
from SunloMusic.lyrics import fetch_lyrics_text, start_live_karaoke
from SunloMusic.keyboards import settings_keyboard

@bot.on_message(filters.command("karaoke") & filters.group)
@catch_errors
@admin_only
async def karaoke_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/karaoke on</code>")
    state = m.command[1].lower()
    
    if state == "on":
        KARAOKE_CHATS.add(m.chat.id)
        q = get_queue(m.chat.id)
        if q.now_playing:
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>")
            q.karaoke_task = asyncio.create_task(start_live_karaoke(bot, m.chat.id, q.now_playing.title, q.now_playing.duration, q))
        else:
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>")
    elif state == "off":
        KARAOKE_CHATS.discard(m.chat.id)
        q = get_queue(m.chat.id)
        if q.karaoke_task:
            q.karaoke_task.cancel()
            q.karaoke_task = None
        await m.reply_text("🎤 <b>Karaoke Mode OFF.</b>")

@bot.on_message(filters.command("autodj") & filters.group)
@catch_errors
@admin_only
async def autodj_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/autodj on</code> or <code>/autodj off</code>")
    
    state = m.command[1].lower()
    if state == "on":
        AUTO_DJ_CHATS.add(m.chat.id)
        await m.reply_text("🎧 <b>Auto-DJ Enabled!</b>")
    elif state == "off":
        AUTO_DJ_CHATS.discard(m.chat.id)
        await m.reply_text("🛑 <b>Auto-DJ Disabled.</b>")

@bot.on_message(filters.command("settings") & filters.group)
@catch_errors
@admin_only
async def settings_cmd(_, m):
    tts_status = m.chat.id in TTS_CHATS
    vsearch_status = m.chat.id in VOICE_CMD_CHATS
    
    text = (
        "⚙️ <b>『 GROUP SETTINGS 』</b> ⚙️\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "🎙️ <b>SunloMusic AI:</b> Bot will announce the song name in VC.\n"
        "🎤 <b>Voice Search:</b> Users can send voice notes to play songs.\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "👇 <i>Click buttons to toggle ON/OFF</i>"
    )
    await m.reply_text(text, reply_markup=settings_keyboard(tts_status, vsearch_status), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex("^toggle_tts$"))
@catch_errors
async def toggle_tts_cb(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    if chat_id in TTS_CHATS:
        TTS_CHATS.discard(chat_id)
        await cq.answer("🔴 SunloMusic AI Voice Disabled")
    else:
        TTS_CHATS.add(chat_id)
        await cq.answer("🟢 SunloMusic AI Voice Enabled")
        
    tts_status = chat_id in TTS_CHATS
    vsearch_status = chat_id in VOICE_CMD_CHATS
    try: await cq.message.edit_reply_markup(reply_markup=settings_keyboard(tts_status, vsearch_status))
    except: pass

@bot.on_callback_query(filters.regex("^toggle_vsearch$"))
@catch_errors
async def toggle_vsearch_cb(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    if chat_id in VOICE_CMD_CHATS:
        VOICE_CMD_CHATS.discard(chat_id)
        await cq.answer("🔴 Voice Search Disabled")
    else:
        VOICE_CMD_CHATS.add(chat_id)
        await cq.answer("🟢 Voice Search Enabled")
        
    tts_status = chat_id in TTS_CHATS
    vsearch_status = chat_id in VOICE_CMD_CHATS
    try: await cq.message.edit_reply_markup(reply_markup=settings_keyboard(tts_status, vsearch_status))
    except: pass

@bot.on_callback_query(filters.regex("^close_settings$"))
@catch_errors
async def close_settings_cb(_, cq: CallbackQuery):
    await cq.message.delete()
    await cq.answer()

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    
    res = await fetch_lyrics_text(query)
    if res: 
        await status.edit_text(f"🎤 <b>{query}</b>\n━━━━━━━━━━━━━\n<blockquote>{res[:4000]}</blockquote>")
    else: 
        await status.edit_text("❌ <b>Lyrics not found in any database.</b>")
