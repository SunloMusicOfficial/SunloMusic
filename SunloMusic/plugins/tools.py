import aiohttp, asyncio, yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.calls import AUTO_DJ_CHATS, play_stream
from SunloMusic.database import set_custom_thumb, del_custom_thumb

@bot.on_message(filters.command("setthumb") & filters.group)
@catch_errors
@admin_only
async def setthumb_cmd(_, m):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply_text("❌ <b>Reply to a photo to set it as thumbnail.</b>")
    file_id = m.reply_to_message.photo.file_id
    await set_custom_thumb(m.chat.id, file_id)
    await m.reply_text("✅ <b>Custom Thumbnail Set!</b>")

@bot.on_message(filters.command("delthumb") & filters.group)
@catch_errors
@admin_only
async def delthumb_cmd(_, m):
    await del_custom_thumb(m.chat.id)
    await m.reply_text("🗑 <b>Custom Thumbnail Removed.</b>")

RADIOS = {
    "lofi": "https://stream.zeno.fm/0r0xa792kwzuv",
    "hindi": "https://stream.zeno.fm/8wv4d0g0tf9uv",
    "english": "https://stream.zeno.fm/0r0xa792kwzuv",
    "punjabi": "https://stream.zeno.fm/0r0xa792kwzuv"
}

@bot.on_message(filters.command("radio") & filters.group)
@catch_errors
@admin_only
async def radio_cmd(_, m):
    buttons = [
        [InlineKeyboardButton("🎧 Lofi Beats", callback_data="rad_lofi"), InlineKeyboardButton("🎵 Bollywood", callback_data="rad_hindi")],
        [InlineKeyboardButton("🎸 English Hits", callback_data="rad_english"), InlineKeyboardButton("🔥 Punjabi", callback_data="rad_punjabi")]
    ]
    await m.reply_text("📻 <b>Select a 24/7 Radio Station:</b>", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("^rad_"))
@catch_errors
async def radio_cb(_, cq):
    key = cq.data.replace("rad_", "")
    if key in RADIOS:
        success = await play_stream(cq.message.chat.id, RADIOS[key])
        if success:
            await cq.message.edit_text(f"📻 <b>Now Streaming:</b> {key.upper()} Radio\n<i>Enjoy 24/7 music!</i>")
        else:
            await cq.answer("❌ Failed to join VC.", show_alert=True)

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={query}") as r:
                data = await r.json()
                if "lyrics" in data:
                    lyrics = data['lyrics'][:4000]
                    await status.edit_text(f"🎤 <b>{data.get('title', query)}</b>\n\n{lyrics}")
                else:
                    await status.edit_text("❌ <b>Lyrics not found.</b>")
    except:
        await status.edit_text("❌ <b>Error fetching lyrics.</b>")

@bot.on_message(filters.command("autodj") & filters.group)
@catch_errors
@admin_only
async def autodj_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/autodj on</code> or <code>/autodj off</code>")
    
    state = m.command[1].lower()
    if state == "on":
        AUTO_DJ_CHATS.add(m.chat.id)
        await m.reply_text("🎧 <b>Auto-DJ Enabled!</b>\nBot will keep playing random songs when queue ends.")
    elif state == "off":
        AUTO_DJ_CHATS.discard(m.chat.id)
        await m.reply_text("🛑 <b>Auto-DJ Disabled.</b>")
