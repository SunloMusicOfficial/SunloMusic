import asyncio, random
from pyrogram import filters
from pyrogram.types import Message, InputMediaPhoto
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import add_coins, add_quiz_score, get_quiz_leaderboard

QUIZ_BANK = [
    {"hint": "🎬 Movie: Kabir Singh • Singer: Arijit Singh\n💭 'Paa liya hain ishq ka imtihaan'", "answer": "tum hi ho", "thumb": "https://i.ytimg.com/vi/Umqb9KENgmk/hqdefault.jpg"},
    {"hint": "🎬 Movie: Brahmastra • Singers: Arijit-Amitabh\n💭 'Kesariya tera ishq hai piya'", "answer": "kesariya", "thumb": "https://i.ytimg.com/vi/BddP6PYo2gs/hqdefault.jpg"},
    {"hint": "🎬 Movie: Animal • Singer: Sonu Nigam\n💭 'Satrangi saari yeh duniya'", "answer": "satrangi", "thumb": "https://i.ytimg.com/vi/2sFq7sE7q7Q/hqdefault.jpg"},
]

active_quizzes = {}

@bot.on_message(filters.command("quiz") & filters.group)
@catch_errors
async def quiz_cmd(_, m: Message):
    chat_id = m.chat.id
    if chat_id in active_quizzes:
        return await m.reply_text("❌ <b>Quiz already running!</b>")
    
    q = random.choice(QUIZ_BANK)
    active_quizzes[chat_id] = {"answer": q["answer"], "started": asyncio.get_running_loop().time()}
    
    # ✅ Poll with Media (Album Art)
    await m.reply_photo(
        q["thumb"],
        caption=f"🎮 <b>MUSIC QUIZ!</b>\n\n{q['hint']}\n\n<b>Guess the song name using /guess</b>\n💰 +10 coins for winner",
    )
    
    async def timeout():
        await asyncio.sleep(60)
        if chat_id in active_quizzes and active_quizzes[chat_id].get("answer") == q["answer"]:
            del active_quizzes[chat_id]
            try: await m.reply_text(f"⏰ <b>Time's up!</b> Answer: <b>{q['answer'].title()}</b>")
            except: pass
    
    asyncio.create_task(timeout())

@bot.on_message(filters.command("guess") & filters.group)
@catch_errors
async def guess_cmd(_, m: Message):
    chat_id = m.chat.id
    if chat_id not in active_quizzes:
        return
    if len(m.command) < 2:
        return await m.reply_text("❌ Usage: <code>/guess song name</code>")
    
    guess = " ".join(m.command[1:]).lower().strip()
    correct = active_quizzes[chat_id]["answer"].lower()
    
    guess_norm = "".join(c for c in guess if c.isalnum() or c == " ")
    correct_norm = "".join(c for c in correct if c.isalnum() or c == " ")
    
    if correct_norm in guess_norm or guess_norm in correct_norm:
        del active_quizzes[chat_id]
        await add_coins(m.from_user.id, 10)
        await add_quiz_score(m.from_user.id, m.from_user.first_name)
        await m.reply_text(f"🎉 <b>CORRECT!</b> {m.from_user.mention} wins!\n🎵 Answer: <b>{correct.title()}</b>\n💰 +10 coins")
    else:
        await m.reply_text(f"❌ <b>Wrong guess!</b> Try again.")
