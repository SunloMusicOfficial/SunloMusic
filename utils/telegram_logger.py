from pyrogram import Client
from config.vars import Config
import traceback

async def send_log(client: Client, text: str):
    if Config.LOG_GROUP_ID:
        try:
            await client.send_message(Config.LOG_GROUP_ID, text)
        except Exception:
            pass

async def log_play(client: Client, message, song_name: str):
    text = (
        f"🎵 **New Play Request**\n\n"
        f"👤 **User:** {message.from_user.mention} [`{message.from_user.id}`]\n"
        f"🗣 **Group:** {message.chat.title} [`{message.chat.id}`]\n"
        f"🎧 **Song:** {song_name}"
    )
    await send_log(client, text)
