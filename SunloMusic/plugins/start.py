from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, m):
    await m.reply_photo(config.START_IMG, caption=f"<b>🎶 Welcome to {config.BOT_NAME}!</b>\n\nUltra-fast VC Music Bot.", reply_markup=start_keyboard()) if config.START_IMG else await m.reply_text(f"<b>🎶 Welcome to {config.BOT_NAME}!</b>", reply_markup=start_keyboard())

@bot.on_message(filters.command("ping"))
async def ping_cmd(_, m):
    await m.reply_text("🏓 <b>Pong! Bot is alive.</b>")
