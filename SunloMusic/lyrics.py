import aiohttp
import re
import asyncio
from urllib.parse import quote
from pyrogram.errors import FloodWait
from SunloMusic.logger import LOGGER

async def _api_get(url, headers, timeout=10):
    try:
        conn = aiohttp.TCPConnector(family=2) # Force IPv4
        async with aiohttp.ClientSession(headers=headers, connector=conn) as s:
            async with s.get(url, timeout=timeout) as r:
                if r.status == 200: return await r.json()
    except Exception as e: LOGGER.error(f"API Error: {e}")
    return None

def _parse_song_info(query: str):
    clean = re.sub(r'[\(\[].*?[\)\]]', '', query)
    parts = [p.strip() for p in re.split(r'[|\-]', clean) if p.strip()]
    if not parts: return query, ""
    title = parts[0]
    artist = parts[1] if len(parts) > 1 else ""
    if " by " in title.lower():
        t_parts = re.split(r' by ', title, flags=re.IGNORECASE)
        title = t_parts[0].strip()
        artist = t_parts[1].strip() if len(t_parts) > 1 else artist
    return title.strip(), artist.strip()

async def fetch_lyrics_text(query: str, duration: int = 0) -> str | None:
    title, artist = _parse_song_info(query)
    headers = {"User-Agent": "SunloMusic/1.0"}
    
    # LRCLIB
    try:
        url = f"https://lrclib.net/api/get?track_name={quote(title)}"
        if artist: url += f"&artist_name={quote(artist)}"
        if duration > 0: url += f"&duration={duration}"
        data = await _api_get(url, headers)
        if data and "plainLyrics" in data and data["plainLyrics"]: return data["plainLyrics"]
        
        search_url = f"https://lrclib.net/api/search?q={quote(title)}"
        if artist: search_url += f"+{quote(artist)}"
        search_data = await _api_get(search_url, headers)
        if search_data and isinstance(search_data, list) and len(search_data) > 0:
            for track in search_data:
                if "plainLyrics" in track and track["plainLyrics"]: return track["plainLyrics"]
    except: pass

    # JioSaavn
    try:
        search_url = f"https://saavnapi-nine.vercel.app/result/?query={quote(title)}"
        data = await _api_get(search_url, headers)
        if data and "songs" in data and "results" in data["songs"] and len(data["songs"]["results"]) > 0:
            lyrics_url = f"https://saavnapi-nine.vercel.app/lyrics/?id={data['songs']['results'][0]['id']}"
            lyrics_data = await _api_get(lyrics_url, headers)
            if lyrics_data and "lyrics" in lyrics_data and lyrics_data["lyrics"]:
                lyrics = re.sub(r'<br\s*/?>', '\n', lyrics_data["lyrics"])
                return re.sub(r'<.*?>', '', lyrics).strip()
    except: pass

    # Lyrics.ovh
    if artist and title:
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            data = await _api_get(url, headers)
            if data and "lyrics" in data and data["lyrics"]: return data["lyrics"]
        except: pass

    return None

async def start_live_karaoke(bot, chat_id, title, duration, q):
    msg = await bot.send_message(chat_id, f"🎤 <b>Fetching live lyrics for:</b> <i>{title}</i>...")
    
    try:
        lyrics = await asyncio.wait_for(fetch_lyrics_text(title, duration), timeout=20.0)
        
        if not lyrics:
            await msg.edit_text(f"🎤 <b>Karaoke:</b> Lyrics not found for <i>{title}</i>.")
            return

        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if not lines: return

        # ✅ Fixed 5 second delay as requested
        delay = 5.0
        header = "🎤 <b>Live Karaoke</b>\n\n<blockquote>"
        accumulated = lines[0]
        
        await msg.edit_text(f"{header}{accumulated}</blockquote>")
        q.karaoke_msg_id = msg.id

        for i in range(1, len(lines)):
            if not q.now_playing or q.now_playing.title != title or q.paused: break
            
            await asyncio.sleep(delay)
            next_line = lines[i]
            
            if len(accumulated) + len(next_line) + len(header) > 4000:
                try: await msg.edit_text(f"{header}{accumulated}</blockquote>")
                except: pass
                accumulated = next_line
                msg = await bot.send_message(chat_id, f"{header}{accumulated}</blockquote>")
                q.karaoke_msg_id = msg.id
            else:
                accumulated += f"\n{next_line}"
                try:
                    await msg.edit_text(f"{header}{accumulated}</blockquote>")
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    try: await msg.edit_text(f"{header}{accumulated}</blockquote>")
                    except: pass
                except Exception:
                    pass

    except asyncio.TimeoutError:
        await msg.edit_text("❌ <b>Karaoke Error:</b> Timed out.")
    except asyncio.CancelledError: pass
    except Exception as e:
        try: await msg.edit_text(f"❌ <b>Karaoke Error:</b> <code>{e}</code>")
        except: pass
