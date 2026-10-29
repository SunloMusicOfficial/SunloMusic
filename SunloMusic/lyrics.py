import aiohttp
import re
import asyncio
from urllib.parse import quote
from SunloMusic.logger import LOGGER

# ✅ Helper for safe API calls with IPv4 & Timeout
async def _api_get(url, headers, timeout=10):
    try:
        conn = aiohttp.TCPConnector(family=2) # Force IPv4
        async with aiohttp.ClientSession(headers=headers, connector=conn) as s:
            async with s.get(url, timeout=timeout) as r:
                if r.status == 200:
                    return await r.json()
    except Exception as e:
        LOGGER.error(f"API Error: {e}")
    return None

def _parse_song_info(query: str):
    """Smart parsing to extract title and artist from messy YouTube titles"""
    # Remove brackets like (Lyrics), [Audio], etc.
    clean = re.sub(r'[\(\[].*?[\)\]]', '', query)
    # Split by | or - to remove extra info
    parts = [p.strip() for p in re.split(r'[|\-]', clean) if p.strip()]
    
    if not parts:
        return query, ""
    
    title = parts[0]
    artist = ""
    
    # If there are multiple parts, the second one is likely the artist/movie
    if len(parts) > 1:
        artist = parts[1]
    
    # If title has "Song by Artist", split it
    if " by " in title.lower():
        title_parts = re.split(r' by ', title, flags=re.IGNORECASE)
        title = title_parts[0].strip()
        artist = title_parts[1].strip() if len(title_parts) > 1 else artist
        
    return title.strip(), artist.strip()

async def fetch_lyrics_text(query: str, duration: int = 0) -> str | None:
    title, artist = _parse_song_info(query)
    LOGGER.info(f"🔎 Parsed -> Title: '{title}', Artist: '{artist}'")
    
    headers = {"User-Agent": "SunloMusic/1.0 (https://github.com/SunloMusicOfficial)"}

    # ✅ 1. LRCLIB API (Best for synced lyrics & exact matches)
    try:
        # Use /api/get for exact match with duration if possible
        params = {"track_name": title}
        if artist: params["artist_name"] = artist
        if duration > 0: params["duration"] = str(duration)
        
        url = f"https://lrclib.net/api/get?track_name={quote(params['track_name'])}"
        if "artist_name" in params: url += f"&artist_name={quote(params['artist_name'])}"
        if "duration" in params: url += f"&duration={params['duration']}"
        
        data = await _api_get(url, headers)
        if data and "plainLyrics" in data and data["plainLyrics"]:
            LOGGER.info("✅ Found on LRCLIB (Exact match)")
            return data["plainLyrics"]
            
        # Fallback to /api/search if exact match fails
        search_url = f"https://lrclib.net/api/search?q={quote(title)}"
        if artist: search_url += f"+{quote(artist)}"
        search_data = await _api_get(search_url, headers)
        if search_data and isinstance(search_data, list) and len(search_data) > 0:
            for track in search_data:
                if "plainLyrics" in track and track["plainLyrics"]:
                    LOGGER.info("✅ Found on LRCLIB (Search match)")
                    return track["plainLyrics"]
    except Exception as e:
        LOGGER.error(f"LRCLIB error: {e}")

    # ✅ 2. JioSaavn API (Best for Bollywood/Punjabi)
    try:
        # Search for song on JioSaavn
        search_url = f"https://saavnapi-nine.vercel.app/result/?query={quote(title)}"
        data = await _api_get(search_url, headers)
        
        if data and "songs" in data and "results" in data["songs"] and len(data["songs"]["results"]) > 0:
            song_id = data["songs"]["results"][0]["id"]
            lyrics_url = f"https://saavnapi-nine.vercel.app/lyrics/?id={song_id}"
            lyrics_data = await _api_get(lyrics_url, headers)
            if lyrics_data and "lyrics" in lyrics_data and lyrics_data["lyrics"]:
                LOGGER.info("✅ Found on JioSaavn")
                # JioSaavn lyrics may contain <br> tags, clean them
                lyrics = re.sub(r'<br\s*/?>', '\n', lyrics_data["lyrics"])
                lyrics = re.sub(r'<.*?>', '', lyrics)
                return lyrics.strip()
    except Exception as e:
        LOGGER.error(f"JioSaavn error: {e}")

    # ✅ 3. Lyrics.ovh (Final Fallback)
    if artist and title:
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            data = await _api_get(url, headers)
            if data and "lyrics" in data and data["lyrics"]:
                LOGGER.info("✅ Found on Lyrics.ovh")
                return data["lyrics"]
        except: pass

    # ✅ 4. Lyrist (Last Resort)
    try:
        encoded = quote(f"{title} {artist}".strip())
        data = await _api_get(f"https://lyrist.vercel.app/api/{encoded}", headers)
        if data and "lyrics" in data and data["lyrics"]:
            LOGGER.info("✅ Found on Lyrist")
            return data["lyrics"]
    except: pass

    LOGGER.error(f"❌ Lyrics not found for {title} - {artist}")
    return None

async def start_live_karaoke(bot, chat_id, title, duration, q):
    msg = await bot.send_message(chat_id, f"🎤 <b>Fetching live lyrics for:</b> <i>{title}</i>...")
    
    try:
        lyrics = await asyncio.wait_for(fetch_lyrics_text(title, duration), timeout=20.0)
        
        if not lyrics:
            await msg.edit_text(f"🎤 <b>Karaoke:</b> Lyrics not found for <i>{title}</i> in database.")
            return

        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if not lines:
            await msg.edit_text(f"🎤 <b>Karaoke:</b> Lyrics content is empty.")
            return

        total_lines = len(lines)
        delay = (duration / total_lines) if duration > 0 else 4.0
        delay = max(3.0, min(delay, 6.0))

        header = "🎤 <b>Live Karaoke</b>\n\n<blockquote>"
        accumulated = lines[0]
        
        # ✅ Send first line
        await msg.edit_text(f"{header}{accumulated}</blockquote>")
        q.karaoke_msg_id = msg.id

        for i in range(1, len(lines)):
            if not q.now_playing or q.now_playing.title != title or q.paused:
                break
            
            await asyncio.sleep(delay)
            
            next_line = lines[i]
            
            # ✅ Telegram limit check (4096 chars)
            if len(accumulated) + len(next_line) + len(header) > 4000:
                # Finalize current message
                try: await msg.edit_text(f"{header}{accumulated}</blockquote>")
                except: pass
                
                # Start new message
                accumulated = next_line
                msg = await bot.send_message(chat_id, f"{header}{accumulated}</blockquote>")
                q.karaoke_msg_id = msg.id
            else:
                # ✅ Append line
                accumulated += f"\n{next_line}"
                try:
                    await msg.edit_text(f"{header}{accumulated}</blockquote>")
                except Exception:
                    pass

    except asyncio.TimeoutError:
        await msg.edit_text("❌ <b>Karaoke Error:</b> Timed out while fetching lyrics.")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await msg.edit_text(f"❌ <b>Karaoke Error:</b> <code>{e}</code>")
