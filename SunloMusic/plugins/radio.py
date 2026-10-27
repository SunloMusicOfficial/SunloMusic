from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.queues import get_queue, Track

RADIOS = {
    "hindi": "https://stream.zeno.fm/0r0xa792kwzuv",
    "english": "https://stream.zeno.fm/8wv4d0g0tf9uv",
    "lofi": "https://stream.zeno.fm/0r0xa792kwzuv",
}

@bot.on_message(filters.command("radio") & filters.group)
@admin_only
async def radio_cmd(_, m):
    if len(m.command) < 2:
        txt = "<b>📻 Available radios:</b>\n\n" + "\n".join(f"• <code>{k}</code>" for k in RADIOS)
        return await m.reply_text(txt + "\n\nUsage: <code>/radio hindi</code>")
    
    key = m.command[1].lower()
    if key not in RADIOS: return await m.reply_text("❌ Unknown radio.")
    
    q = get_queue(m.chat.id)
    q.now_playing = Track(title=f"Radio: {key}", url=RADIOS[key], duration=0, thumbnail="", requester=m.from_user.first_name)
    
    success = await play_stream(m.chat.id, RADIOS[key])
    if success:
        await m.reply_text(f"📻 <b>Now streaming:</b> {key}")
    else:
        q.now_playing = None
        await m.reply_text("❌ <b>Failed to join VC. Start the voice chat first.</b>")
