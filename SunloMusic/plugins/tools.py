import aiohttp, asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only

KARAOKE_CHATS = set()

@bot.on_message(filters.command("karaoke") & filters.group)
@catch_errors
@admin_only
async def karaoke_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/karaoke on</code>")
    state = m.command[1].lower()
    if state == "on":
        KARAOKE_CHATS.add(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode ON!</b>")
    elif state == "off":
        KARAOKE_CHATS.discard(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode OFF.</b>")

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    try:
        # ✅ New Reliable Lyrics API
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://lyrist.vercel.app/api/{query}") as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data:
                        lyrics = data['lyrics'][:4000]
                        return await status.edit_text(f"🎤 <b>{data.get('title', query)} - {data.get('artist', '')}</b>\n\n{lyrics}")
        await status.edit_text("❌ <b>Lyrics not found.</b>")
    except:
        await status.edit_text("❌ <b>Error fetching lyrics.</b>")
