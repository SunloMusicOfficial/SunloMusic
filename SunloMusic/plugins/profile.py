import os
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, sudo_only
from SunloMusic.logger import LOGGER

@bot.on_message(filters.command("setprofilepic"))
@catch_errors
@sudo_only
async def setprofilepic_cmd(_, m: Message):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply_text("❌ <b>Reply to a photo to set as bot profile pic.</b>")
    
    status = await m.reply_text("📸 <b>Setting profile picture...</b>")
    try:
        photo = await m.reply_to_message.download()
        await bot.set_profile_photo(photo=photo)
        await status.edit_text("✅ <b>Profile picture updated!</b>")
    except Exception as e:
        await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")
    finally:
        if os.path.exists(photo): os.remove(photo)

@bot.on_message(filters.command("delprofilepic"))
@catch_errors
@sudo_only
async def delprofilepic_cmd(_, m: Message):
    status = await m.reply_text("🗑 <b>Removing profile picture...</b>")
    try:
        photos = await bot.get_profile_photos("me")
        if photos:
            await bot.delete_profile_photos([p.file_id for p in photos])
        await status.edit_text("✅ <b>Profile picture removed!</b>")
    except Exception as e:
        await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")

@bot.on_message(filters.command("profileaudio"))
@catch_errors
async def profileaudio_cmd(_, m: Message):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    try:
        audios = await bot.get_user_profile_audios(target.id)
        if audios:
            await m.reply_audio(audios[0].file_id, caption=f"🎵 <b>{target.first_name}'s Profile Audio</b>")
        else:
            await m.reply_text("❌ <b>No profile audio found.</b>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>")

@bot.on_message(filters.command("settag") & filters.group)
@catch_errors
async def settag_cmd(_, m: Message):
    if len(m.command) < 3:
        return await m.reply_text("❌ <b>Usage:</b> <code>/settag @user TagName</code>")
    try:
        target = m.reply_to_message.from_user if m.reply_to_message else m.command[1]
        tag = m.command[-1][:16]  # Max 16 chars
        await bot.set_chat_member_tag(m.chat.id, target.id, tag)
        await m.reply_text(f"✅ <b>Tag set to:</b> <code>{tag}</code>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>")
