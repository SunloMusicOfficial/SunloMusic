import time
from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, start_next_song
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT
from SunloMusic.keyboards import player_keyboard
from pyrogram import enums

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@catch_errors
async def skip_cmd(_, m):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    
    user = m.from_user
    is_admin = False
    if await is_sudo(user.id): is_admin = True
    else:
        try:
            member = await m.chat.get_member(user.id)
            if member.privileges and (member.privileges.can_manage_voice_chats or member.privileges.can_manage_chat): is_admin = True
        except: pass
        
    if is_admin:
        return await start_next_song(m.chat.id, q)
        
    # Vote Skip Logic
    if user.id in q.votes:
        return await m.reply_text("🗳️ You have already voted to skip!")
        
    q.votes.add(user.id)
    
    try:
        participants = await m.chat.get_members(filter=enums.ChatMembersFilter.VOICE_CHAT)
        total_listeners = len(participants) - 2 # Exclude Bot & Assistant
    except:
        total_listeners = 5 # Fallback
        
    votes_needed = max(1, int(total_listeners / 2))
    current_votes = len(q.votes)
    
    if current_votes >= votes_needed:
        await m.reply_text(f"🗳️ <b>Vote Skip Passed!</b> ({current_votes}/{votes_needed})\nSkipping...")
        await start_next_song(m.chat.id, q)
    else:
        await m.reply_text(f"🗳️ <b>Vote Added!</b>\nNeeded: {votes_needed - current_votes} more votes to skip.")
