import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("lyrics"))
async def lyrics_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status = await message.reply_text("🔍 **Searching for lyrics...**")
    
    try:
        # Using a public lyrics API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-lyrics-api.com/search?q={query}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lyrics = data.get("lyrics", "Lyrics not found.")
                    
                    if len(lyrics) > 4000:
                        lyrics = lyrics[:3990] + "..."
                        
                    await status.edit_text(f"📝 **Lyrics for {query}**\n\n{lyrics}")
                else:
                    await status.edit_text("❌ Lyrics not found.")
    except Exception:
        await status.edit_text("❌ Error fetching lyrics.")
