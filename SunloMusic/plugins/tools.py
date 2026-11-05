import asyncio
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS, AUTO_DJ_CHATS, CROSSFADE_CHATS, get_queue
from SunloMusic.lyrics import fetch_lyrics_text, start_live_karaoke
from SunloMusic.keyboards import settings_keyboard
from SunloMusic.database import get_group_setting, set_group_setting

@bot.on_message(filters.command("crossfade") & filters.group)
@catch_errors
@admin_only
async def crossfade_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ Usage: <code>/crossfade on</code> or <code>off</code>")
    state = m.command[1].lower()
    if state == "on":
        CROSSFADE_CHATS.add(m.chat.id)
        await m.reply_text("✨ <b>Crossfade Enabled!</b>")
    elif state == "off":
        CROSSFADE_CHATS.discard(m.chat.id)
        await m.reply_text("🔇 <b>Crossfade Disabled.</b>")

@bot.on_message(filters.command("settings") & filters.group)
@catch_errors
@admin_only
async def settings_cmd(_, m):
    tts_status = await get_group_setting(m.chat.id, "tts", False)
    vsearch_status = await get_group_setting(m.chat.id, "vsearch", False)
    text = "⚙️ <b>『 GROUP SETTINGS 』</b> ⚙️\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n🎙️ <b>AI Voice:</b> Announce song name.\n🎤 <b>Voice Search:</b> Play via voice notes.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    await m.reply_text(text, reply_markup=settings_keyboard(tts_status, vsearch_status), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex("^toggle_(tts|vsearch)$"))
@catch_errors
async def toggle_cb(_, cq: CallbackQuery):
    key = "tts" if "tts" in cq.data else "vsearch"
    current = await get_group_setting(cq.message.chat.id, key, False)
    await set_group_setting(cq.message.chat.id, key, not current)
    await cq.answer(f"{'🟢 Enabled' if not current else '🔴 Disabled'}")
    tts = await get_group_setting(cq.message.chat.id, "tts", False)
    vs = await get_group_setting(cq.message.chat.id, "vsearch", False)
    try: await cq.message.edit_reply_markup(reply_markup=settings_keyboard(tts, vs))
    except: pass

@bot.on_callback_query(filters.regex("^close_settings$"))
@catch_errors
async def close_settings_cb(_, cq: CallbackQuery):
    await cq.message.delete(); await cq.answer()
