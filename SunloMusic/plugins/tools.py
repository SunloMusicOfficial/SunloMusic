import aiohttp, asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS

async def fetch_lyrics_text(query: str) -> str | None:
    # Clean title (remove "(Official Video)" etc) for better search
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].strip()
    
    # ✅ API 1: Lyrist
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://lyrist.vercel.app/api/{clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass

    # ✅ API 2: Some-Random-API
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass
    
    return None

async def send_karaoke(chat_id: int, title: str):
    lyrics = await fetch_lyrics_text(title)
    if lyrics:
        try: await bot.send_message(chat_id, lyrics)
        except: pass

@bot.on_message(filters.command("karaoke") & filters.group)
@catch_errors
@admin_only
async def karaoke_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/karaoke on</code>")
    state = m.command[1].lower()
    if state == "on":
        KARAOKE_CHATS.add(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode ON!</b>\nBot will automatically send lyrics for every song.")
    elif state == "off":
        KARAOKE_CHATS.discard(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode OFF.</b>")

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    res = await fetch_lyrics_text(query)
    if res:
        await status.edit_text(res)
    else:
        await status.edit_text("❌ <b>Lyrics not found in any database.</b>")
