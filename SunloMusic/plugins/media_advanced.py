import os
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import download_media_file
from pyrogram.enums import ButtonStyle

@bot.on_message(filters.command("videoq") & filters.group)
@catch_errors
async def video_quality_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("Usage: /videoq song name")
    
    query = " ".join(m.command[1:])
    await m.reply_text(
        f"🎬 <b>Select Video Quality for:</b> <code>{query}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("144p", callback_data=f"vq_144_{query}", style=ButtonStyle.PRIMARY), InlineKeyboardButton("360p", callback_data=f"vq_360_{query}", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("720p", callback_data=f"vq_720_{query}", style=ButtonStyle.SUCCESS), InlineKeyboardButton("1080p", callback_data=f"vq_1080_{query}", style=ButtonStyle.SUCCESS)]
        ])
    )

@bot.on_message(filters.command("livephoto"))
@catch_errors
async def livephoto_cmd(_, m: Message):
    if not m.reply_to_message or not m.reply_to_message.video:
        return await m.reply_text("❌ Reply to a short video (max 5 sec) to send as Live Photo.")
    
    # Telegram Live Photo format (video with sound)
    await m.reply_to_message.copy(m.chat.id, has_spoiler=False)

@bot.on_message(filters.command("getfile") & filters.group)
@catch_errors
async def get_file_link_cmd(_, m: Message):
    if not m.reply_to_message or not m.reply_to_message.document:
        return await m.reply_text("❌ Reply to a document to get its link.")
    
    doc = m.reply_to_message.document
    # Bot API 10.3 - tg://document?id= links
    link = f"tg://document?id={doc.file_id}"
    await m.reply_text(
        f"📄 <b>File Link:</b>\n<code>{link}</code>\n\n"
        f"<i>Tap to copy. Works in Telegram internal browser.</i>"
    )

# 1-on-1 Topics (Bot API 9.4)
@bot.on_message(filters.command("createtopic") & filters.private)
@catch_errors
async def create_topic_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("Usage: /createtopic Topic Name")
    try:
        topic = await bot.create_forum_topic(m.chat.id, m.command[1])
        await m.reply_text(f"✅ Topic created: {topic.title}")
    except Exception as e:
        await m.reply_text(f"❌ Failed (requires forum-enabled bot): {e}")
