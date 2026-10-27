from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only

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
    if key not in RADIOS:
        return await m.reply_text("❌ Unknown radio.")
    await play_stream(m.chat.id, RADIOS[key])
    await m.reply_text(f"📻 <b>Now streaming:</b> {key}")
