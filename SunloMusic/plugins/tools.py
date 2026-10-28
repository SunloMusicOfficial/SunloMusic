import aiohttp, asyncio, yt_dlp
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.calls import AUTO_DJ_CHATS

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
                    lyrics = data['lyrics'][:4000] # Limit to 4000 chars
                    await status.edit_text(f"🎤 <b>{data.get('title', query)}</b>\n\n{lyrics}")
                else:
                    await status.edit_text("❌ <b>Lyrics not found.</b>")
    except Exception as e:
        await status.edit_text(f"❌ <b>Error fetching lyrics.</b>")

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
    else:
        await m.reply_text("❌ Invalid option. Use 'on' or 'off'.")
