from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.config import config
from groq import Groq

groq_client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None

@bot.on_message(filters.group & filters.text & ~filters.command(["play", "vplay", "skip", "stop", "pause", "resume", "seek", "song", "video", "search", "help", "allcommand", "settings", "id", "gstats", "settag", "clearreactions", "delreaction"]))
@catch_errors
async def ai_chat_handler(_, m: Message):
    if not groq_client or not config.GROQ_API_KEY: return
    
    # Trigger only if bot is mentioned or replied
    is_mention = m.text and f"@{bot.me.username}" in m.text
    is_reply = m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.id == bot.me.id
    
    if not (is_mention or is_reply): return
    
    query = m.text.replace(f"@{bot.me.username}", "").strip()
    if not query: return
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are SunloMusic, a premium Telegram music bot. Reply in a friendly, short, and helpful way in Hinglish (Hindi + English)."},
                {"role": "user", "content": query}
            ],
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content
        await m.reply_text(f"🤖 {reply}")
    except Exception as e:
        pass
