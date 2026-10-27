import asyncio, yt_dlp
YDL_OPTS = {"format": "bestaudio/best", "quiet": True, "noplaylist": True, "nocheckcertificate": True}

def _extract_sync(query: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(query if query.startswith("http") else f"ytsearch1:{query}", download=False)
            if "entries" in info: info = info["entries"][0]
            return {"title": info.get("title", "Unknown"), "url": info.get("url"), "duration": int(info.get("duration") or 0), "thumbnail": info.get("thumbnail", "")}
    except Exception: return None

async def extract_audio(query: str):
    return await asyncio.get_event_loop().run_in_executor(None, _extract_sync, query)
