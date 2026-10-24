import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from core.call import sunlo_call
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from database.mongodb import db
from core.player import clear_queue

TRIVIA_SONGS = [
    "Tum Hi Ho", "Chaleya", "Kesariya", "Shape of You",
    "Believer", "Despacito", "Zaalima", "Kabira", 
    "Faded", "Pasoori", "Apna Bana Le", "Let Me Down Slowly"
]

ACTIVE_GAMES = {}

@Client.on_message(filters.command(["guess", "trivia"]) & filters.group)
async def guess_game_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in ACTIVE_GAMES:
        return await message.reply_text("⚠️ **Game is already running!** Listen to the VC.")

    status = await message.reply_text("🎮 **Starting Music Trivia...**\nFetching a random song...")
    
    song_name = random.choice(TRIVIA_SONGS)
    track_data = await fetch_audio_url(f"{song_name} audio")
    
    if not track_data:
        return await status.edit_text("❌ Failed to start game, try again.")

    ACTIVE_GAMES[chat_id] = song_name.lower()
    
    try:
        # Trivia track play karna bina queue disturb kiye
        await sunlo_call.play(chat_id, AudioPiped(track_data["stream_url"]))
        await status.edit_text(
            "🎧 **GUESS THE SONG!**\n\n"
            "🔊 Listen to the Voice Chat!\n"
            "💬 Type the exact name of the song in the chat to win.\n\n"
            "⏱ **Time Limit:** 20 Seconds\n"
            "🎁 **Prize:** 500 Sunlo Coins 🪙"
        )
        
        # 20 seconds ka timer
        await asyncio.sleep(20)
        
        if chat_id in ACTIVE_GAMES: # Agar kisi ne guess nahi kiya
            del ACTIVE_GAMES[chat_id]
            await client.send_message(chat_id, f"⏰ **Time's Up!**\nNo one guessed it correctly.\n\nThe song was: **{song_name}**")
            await sunlo_call.leave_call(chat_id)
            clear_queue(chat_id)
            
    except Exception as e:
        if chat_id in ACTIVE_GAMES: del ACTIVE_GAMES[chat_id]
        await status.edit_text(f"❌ Error starting game: {e}")

# Text monitor to check answers
@Client.on_message(filters.text & filters.group, group=10)
async def check_guess(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in ACTIVE_GAMES:
        correct_ans = ACTIVE_GAMES[chat_id]
        if correct_ans in message.text.lower():
            del ACTIVE_GAMES[chat_id]
            
            # Winner ko coins dena
            await db.add_coins(message.from_user.id, 500)
            
            await message.reply_text(
                f"🎉 **WINNER!** 🎉\n\n"
                f"👤 {message.from_user.mention} guessed the song correctly!\n"
                f"🎵 **Answer:** {correct_ans.title()}\n\n"
                f"🎁 **500 Coins** have been added to your wallet! 🪙"
            )
            
            # Game khatam hone par VC stop kar dena
            try:
                await sunlo_call.leave_call(chat_id)
                clear_queue(chat_id)
            except:
                pass
