from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.logger import LOGGER

@bot.on_message(filters.command("clearreactions") & filters.group)
@catch_errors
@admin_only
async def clearreactions_cmd(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("❌ <b>Reply to a message to clear its reactions.</b>")
    
    try:
        await bot.delete_all_message_reactions(m.chat.id, m.reply_to_message.id)
        await m.reply_text("🗑 <b>All reactions cleared!</b>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>")

@bot.on_message(filters.command("delreaction") & filters.group)
@catch_errors
@admin_only
async def delreaction_cmd(_, m: Message):
    if len(m.command) < 2 or not m.reply_to_message:
        return await m.reply_text("❌ <b>Usage:</b> Reply to a message with <code>/delreaction 👍</code>")
    
    try:
        await bot.delete_message_reaction(m.chat.id, m.reply_to_message.id, m.command[1])
        await m.reply_text("✅ <b>Reaction removed!</b>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>")
