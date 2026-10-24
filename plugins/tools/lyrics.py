import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.logger import LOGGER

@Client.on_message(filters.command(["lyrics", "ly"]) & filters.group)
async def lyrics_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 **Searching for lyrics...**")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Using Some-Random-API for free lyrics fetching
            async with session.get(f"https://some-random-api.com/lyrics?title={query}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    title = data.get("title", query)
                    artist = data.get("author", "Unknown Artist")
                    lyrics = data.get("lyrics", "")
                    
                    if not lyrics:
                        return await status_msg.edit_text("❌ **Lyrics not found!**")
                        
                    lyrics_text = f"🎤 **{title}**\n👤 **Artist:** {artist}\n\n{lyrics}"
                    
                    # Telegram ki 4096 character limit handle karna
                    if len(lyrics_text) > 4096:
                        await status_msg.edit_text(lyrics_text[:4093] + "...")
                    else:
                        await status_msg.edit_text(lyrics_text)
                else:
                    await status_msg.edit_text("❌ **Lyrics not found for this song!**")
    except Exception as e:
        LOGGER.error(f"Lyrics API Error: {e}")
        await status_msg.edit_text("❌ **Error fetching lyrics.**")
