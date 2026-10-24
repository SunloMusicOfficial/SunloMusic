from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from core.call import sunlo_call
from core.player import get_next_track, clear_queue

@Client.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    next_track = get_next_track(chat_id)
    
    if next_track:
        await sunlo_call.play(chat_id, AudioPiped(next_track["stream_url"]))
        await message.reply_text(f"⏭ **Skipped! Playing next:**\n🎵 **{next_track['title']}**")
    else:
        await sunlo_call.leave_call(chat_id)
        clear_queue(chat_id)
        await message.reply_text("⏭ **Skipped! Queue is empty, leaving VC.**")

@Client.on_message(filters.command("pause") & filters.group)
async def pause_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await sunlo_call.pause_stream(chat_id)
        await message.reply_text("⏸ **Stream paused!**")
    except:
        await message.reply_text("❌ **Nothing is playing to pause.**")

@Client.on_message(filters.command("resume") & filters.group)
async def resume_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await sunlo_call.resume_stream(chat_id)
        await message.reply_text("▶️ **Stream resumed!**")
    except:
        await message.reply_text("❌ **Nothing is paused to resume.**")
