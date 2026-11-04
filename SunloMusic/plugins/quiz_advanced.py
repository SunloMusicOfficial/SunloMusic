from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors

@bot.on_message(filters.command("quizpoll") & filters.group)
@catch_errors
async def advanced_quiz_cmd(_, m: Message):
    # Advanced Poll: Multiple Answers, Hidden Results
    await bot.send_poll(
        chat_id=m.chat.id,
        question="🎵 Which of these are Arijit Singh songs?",
        options=["Kesariya", "Tum Hi Ho", "Shape of You", "Chaleya"],
        type="quiz",
        correct_option_id=0, # We can use multiple correct, but Telegram quiz type requires 1. For multi, use type="regular"
        is_anonymous=True,
        allows_multiple_answers=True,
        explanation="Kesariya, Tum Hi Ho, and Chaleya are Arijit Singh songs."
    )
    await m.reply_text("☝️ Vote in the poll above!")
