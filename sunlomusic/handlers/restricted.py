# Copyright (C) @YO_UR_OFFICIAL_CRUSH
import os
import re
import time
import math
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from sunlomusic.core.logging import logger
from sunlomusic.core.config import Config

# Utility for Progress Bar
async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        progress = "[{0}{1}] \nPercentage: {2}% \nDone: {3} \nTotal: {4} \nSpeed: {5}/s \nETA: {6}".format(
            ''.join(["●" for i in range(math.floor(percentage / 5))]),
            ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            TimeFormatter(time_to_completion)
        )
        try:
            await message.edit(f"**{ud_type}**\n\n{progress}")
        except:
            pass

def humanbytes(size):
    if not size: return "0 B"
    power = 2**10
    n = 0
    dict = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {dict[n]}"

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] if tmp else "0s"

LINK_REGEX = r"(https?://)?(t\.me|telegram\.me)/(?:(c)/(\d+)|([a-zA-Z0-9_]+))/(\d+)(?:-(\d+))?"

def extract_link_info(link):
    match = re.search(LINK_REGEX, link)
    if not match:
        return None, None, None
    is_private = match.group(4) is not None
    if is_private:
        chat_id = int(f"-100{match.group(4)}")
    else:
        chat_id = match.group(5)
    
    start_id = int(match.group(6))
    end_id = int(match.group(7)) if match.group(7) else start_id
    return chat_id, start_id, end_id

def register_restricted_handlers(app: Client, user_client: Client):
    @app.on_message(filters.command("dl"))
    async def download_restricted(client, message: Message):
        if len(message.command) < 2:
            await message.reply_text("**Usage:** `/dl <t.me link>`\nExample: `/dl https://t.me/c/123456789/1-5`")
            return
        
        link = message.command[1]
        chat_id, start_id, end_id = extract_link_info(link)
        
        if not chat_id:
            await message.reply_text("**Invalid Telegram link.**")
            return
        
        total_files = end_id - start_id + 1
        status_msg = await message.reply_text(f"**⏳ Processing {total_files} file(s)...**")
        c_time = time.time()
        
        for msg_id in range(start_id, end_id + 1):
            try:
                target_msg = await user_client.get_messages(chat_id, msg_id)
                if not target_msg or not target_msg.media:
                    continue
                
                file_path = await user_client.download_media(
                    target_msg, 
                    progress=progress_for_pyrogram, 
                    progress_args=(f"Downloading {msg_id}", status_msg, c_time)
                )
                
                if file_path:
                    await status_msg.edit(f"**⬆️ Uploading {msg_id}...**")
                    if target_msg.video:
                        await app.send_video(message.chat.id, file_path, caption=target_msg.caption, progress=progress_for_pyrogram, progress_args=("Uploading", status_msg, c_time))
                    elif target_msg.audio:
                        await app.send_audio(message.chat.id, file_path, caption=target_msg.caption, progress=progress_for_pyrogram, progress_args=("Uploading", status_msg, c_time))
                    else:
                        await app.send_document(message.chat.id, file_path, caption=target_msg.caption, progress=progress_for_pyrogram, progress_args=("Uploading", status_msg, c_time))
                    
                    os.remove(file_path)
                
                c_time = time.time()
                await asyncio.sleep(1) # Prevent FloodWait
                
            except Exception as e:
                logger.error(f"Error downloading {msg_id}: {e}")
                continue
                
        await status_msg.edit(f"**✅ Successfully downloaded {total_files} file(s).**")
