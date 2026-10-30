import asyncio, random
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import add_coins, add_quiz_score, get_quiz_leaderboard

QUIZ_BANK = [
    {"hint": "🎬 Movie: Kabir Singh • Singer: Arijit Singh\n💭 'Paa liya hain ishq ka imtihaan'", "answer": "tum hi ho"},
    {"hint": "🎬 Movie: Brahmastra • Singers: Arijit-Amitabh\n💭 'Kesariya tera ishq hai piya'", "answer": "kesariya"},
    {"hint": "🎬 Movie: Animal • Singer: Sonu Nigam\n💭 'Satrangi saari yeh duniya'", "answer": "satrangi"},
    {"hint": "🎬 Movie: Shershaah • Singer: B Praak\n💭 'Ranjha ranjha kardi ve main'", "answer": "ranjha"},
    {"hint": "🎬 Movie: Aashiqui 2 • Singer: Arijit Singh\n💭 'Hum tere bin ab reh nahi sakte'", "answer": "sun raha hai na tu"},
    {"hint": "🎬 Movie: Jab We Met • Singer: Mohit Chauhan\n💭 'Tum se hi din hota hai'", "answer": "tum se hi"},
    {"hint": "🎬 Movie: Ae Dil Hai Mushkil • Singer: Arijit\n💭 'Tu safar mera, hai tu hi meri manzil'", "answer": "ae dil hai mushkil"},
    {"hint": "🎬 Movie: Chennai Express • Singer: Honey Singh\n💭 'Lungi dance, lungi dance'", "answer": "lungi dance"},
    {"hint": "🎬 Movie: Bajirao Mastani • Singer: Shreya Ghoshal\n💭 'Deewani Mastani, ho gayi'", "answer": "deewani mastani"},
    {"hint": "🎬 Movie: Dangal • Singer: Daler Mehndi\n💭 'Dhaakad dhaakad, aankh se dhaakad'", "answer": "dhaakad"},
    {"hint": "🎬 Movie: Kal Ho Naa Ho • Singer: Sonu Nigam\n💭 'Har ghadi badal rahi hai roop zindagi'", "answer": "kal ho naa ho"},
    {"hint": "🎬 Movie: Dilwale • Singer: Arijit Singh\n💭 'Janam janam, janam janam, saath chalte'", "answer": "janam janam"},
]

active_quizzes = {}

@bot.on_message(filters.command("quiz") & filters.group)
@catch_errors
async def quiz_cmd(_, m: Message):
    chat_id = m.chat.id
    if chat_id in active_quizzes:
        return await m.reply_text("❌ <b>Quiz already running in this chat!</b>")
    
    q = random.choice(QUIZ_BANK)
    active_quizzes[chat_id] = {"hint": q["hint"], "answer": q["answer"], "started": asyncio.get_running_loop().time()}
    
    await m.reply_text(
        f"🎮 <b>MUSIC QUIZ!</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"{q['hint']}\n"
        f"━━━━━━━━━━━━━\n"
        f"<b>Guess the song name!</b>\n"
        f"Use <code>/guess song name</code>\n"
        f"⏱ <i>60 seconds to answer</i>\n"
        f"💰 <i>+10 coins for winner</i>"
    )
    
    async def timeout():
        await asyncio.sleep(60)
        if chat_id in active_quizzes and active_quizzes[chat_id].get("answer") == q["answer"]:
            del active_quizzes[chat_id]
            try:
                await m.reply_text(f"⏰ <b>Time's up!</b>\n\nAnswer was: <b>{q['answer'].title()}</b>")
            except: pass
    
    asyncio.create_task(timeout())

@bot.on_message(filters.command("guess") & filters.group)
@catch_errors
async def guess_cmd(_, m: Message):
    chat_id = m.chat.id
    if chat_id not in active_quizzes:
        return
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/guess song name</code>")
    
    guess = " ".join(m.command[1:]).lower().strip()
    correct = active_quizzes[chat_id]["answer"].lower()
    
    # Normalize
    guess_norm = "".join(c for c in guess if c.isalnum() or c == " ")
    correct_norm = "".join(c for c in correct if c.isalnum() or c == " ")
    
    # Fuzzy match - bigram containment
    if correct_norm in guess_norm or guess_norm in correct_norm:
        del active_quizzes[chat_id]
        await add_coins(m.from_user.id, 10)
        await add_quiz_score(m.from_user.id, m.from_user.first_name)
        await m.reply_text(
            f"🎉 <b>CORRECT!</b> {m.from_user.mention} wins!\n"
            f"━━━━━━━━━━━━━\n"
            f"🎵 Answer: <b>{correct.title()}</b>\n"
            f"💰 Reward: <b>+10 coins</b>"
        )
    else:
        await m.reply_text(f"❌ <b>Wrong guess!</b> {m.from_user.mention} Try again.")

@bot.on_message(filters.command("quizlb") & filters.group)
@catch_errors
async def quizlb_cmd(_, m: Message):
    lb = await get_quiz_leaderboard(limit=10)
    if not lb:
        return await m.reply_text("📊 <b>No quiz winners yet!</b> Start with /quiz")
    
    text = "<b>🏆 Quiz Champions</b>\n━━━━━━━━━━━━━\n"
    for i, u in enumerate(lb, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{emoji} {u.get('name', 'Unknown')} — <code>{u.get('wins', 0)}</code> wins\n"
    
    await m.reply_text(text)
