from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pytgcalls.types import AudioPiped
from core.call import sunlo_call
from core.player import get_next_track, clear_queue

# --- TEXT COMMANDS ---
@Client.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client: Client, message: Message):
    await skip_logic(client, message.chat.id, message)

@Client.on_message(filters.command("stop") & filters.group)
async def stop_cmd(client: Client, message: Message):
    await stop_logic(client, message.chat.id, message)

# --- CALLBACK QUERIES (BUTTON CLICKS) ---
@Client.on_callback_query(filters.regex("^pause_cb$"))
async def pause_cb(client: Client, cq: CallbackQuery):
    try:
        await sunlo_call.pause_stream(cq.message.chat.id)
        await cq.answer("⏸ Stream paused!", show_alert=True)
    except:
        await cq.answer("Nothing is playing!", show_alert=True)

@Client.on_callback_query(filters.regex("^resume_cb$"))
async def resume_cb(client: Client, cq: CallbackQuery):
    try:
        await sunlo_call.resume_stream(cq.message.chat.id)
        await cq.answer("▶️ Stream resumed!", show_alert=True)
    except:
        await cq.answer("Nothing is paused!", show_alert=True)

@Client.on_callback_query(filters.regex("^skip_cb$"))
async def skip_cb_func(client: Client, cq: CallbackQuery):
    await skip_logic(client, cq.message.chat.id, cq)

@Client.on_callback_query(filters.regex("^stop_cb$"))
async def stop_cb_func(client: Client, cq: CallbackQuery):
    await stop_logic(client, cq.message.chat.id, cq)

# --- CORE LOGIC FUNCTIONS ---
async def skip_logic(client, chat_id, update_obj):
    next_track = get_next_track(chat_id)
    if next_track:
        await sunlo_call.play(chat_id, AudioPiped(next_track["stream_url"]))
        msg = f"⏭ **Skipped! Playing next:**\n🎵 **{next_track['title']}**"
        if isinstance(update_obj, Message): await update_obj.reply_text(msg)
        else: await update_obj.message.reply_text(msg); await update_obj.answer("Skipped!")
    else:
        await sunlo_call.leave_call(chat_id)
        clear_queue(chat_id)
        msg = "⏭ **Skipped! Queue is empty, leaving VC.**"
        if isinstance(update_obj, Message): await update_obj.reply_text(msg)
        else: await update_obj.message.reply_text(msg); await update_obj.answer("Queue Empty, Left VC!")

async def stop_logic(client, chat_id, update_obj):
    try:
        await sunlo_call.leave_call(chat_id)
        clear_queue(chat_id)
        msg = "⏹ **Stream stopped and queue cleared!**"
        if isinstance(update_obj, Message): await update_obj.reply_text(msg)
        else: await update_obj.message.reply_text(msg); await update_obj.answer("Stopped!")
    except:
        pass
