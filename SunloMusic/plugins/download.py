import asyncio, os
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import add_coins, get_coins, spend_coins
from SunloMusic.ytdlp import download_media_file, cleanup_download
from SunloMusic.logger import LOGGER
from SunloMusic.config import config

DOWNLOAD_COST = 5  # 5 coins per download

def _fmt_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

@bot.on_message(filters.command("song") & ~filters.private)
@catch_errors
async def song_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/song song name or URL</code>")
    await _do_download(m, video=False)

@bot.on_message(filters.command("video") & ~filters.private)
@catch_errors
async def video_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/video song name or URL</code>")
    await _do_download(m, video=True)

async def _do_download(m: Message, video: bool):
    user_id = m.from_user.id
    query = " ".join(m.command[1:])
    
    # Coins check (skip for sudo/owner)
    from SunloMusic.database import is_sudo
    is_priv = await is_sudo(user_id)
    if not is_priv:
        bal = await get_coins(user_id)
        if bal < DOWNLOAD_COST:
            return await m.reply_text(
                f"❌ <b>Not enough coins!</b>\n\n"
                f"💰 Your balance: <code>{bal}</code>\n"
                f"💵 Needed: <code>{DOWNLOAD_COST}</code>\n\n"
                f"Use /daily to claim coins!"
            )
    
    status = await m.reply_text(f"🔍 <b>Searching & downloading {'video' if video else 'audio'}...</b>\nThis may take a minute.")
    
    try:
        result = await download_media_file(query, video=video, max_duration=1800)
    except Exception as e:
        LOGGER.error(f"Download error: {e}")
        return await status.edit_text(f"❌ <b>Download failed:</b> <code>{e}</code>")
    
    if not result or not result.get("path") or not os.path.exists(result["path"]):
        return await status.edit_text("❌ <b>Could not download the file.</b>\nTry a different query or URL.")
    
    file_path = result["path"]
    title = result["title"]
    duration = result["duration"]
    
    try:
        file_size = os.path.getsize(file_path)
        
        # Telegram bot limit is 2GB
        if file_size > 2 * 1024 * 1024 * 1024:
            return await status.edit_text("❌ <b>File too large (over 2GB).</b>")
        
        await status.edit_text(f"📤 <b>Uploading:</b> {title[:50]}\n📦 Size: {_fmt_size(file_size)}")
        
        from pyrogram.types import InputMediaAudio, InputMediaVideo
        
        try:
            await m.reply_audio(
                audio=file_path,
                title=title[:64],
                performer="SunloMusic",
                duration=duration,
                caption=f"🎵 <b>{title}</b>\n\n🤖 Downloaded by @{config.BOT_USERNAME.strip('@')}"
            )
        except Exception as e:
            LOGGER.error(f"reply_audio failed: {e}, trying as document")
            await m.reply_document(
                document=file_path,
                caption=f"🎵 <b>{title}</b>\n\n🤖 Downloaded by @{config.BOT_USERNAME.strip('@')}"
            )
        
        # Deduct coins
        if not is_priv:
            await spend_coins(user_id, DOWNLOAD_COST)
            await status.delete()
            await m.reply_text(f"✅ <b>Done!</b> ({DOWNLOAD_COST} coins deducted)")
        else:
            await status.delete()
    except Exception as e:
        LOGGER.error(f"Upload error: {e}")
        await status.edit_text(f"❌ <b>Upload failed:</b> <code>{str(e)[:200]}</code>")
    finally:
        cleanup_download(file_path)
