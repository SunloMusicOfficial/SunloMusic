from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, sudo_only
from SunloMusic.database import get_group_setting, set_group_setting
from SunloMusic.logger import LOGGER

@bot.on_message(filters.command("whitelist") & filters.private)
@catch_errors
@sudo_only
async def whitelist_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text(
            "❌ <b>Usage:</b>\n"
            "<code>/whitelist add user_id</code>\n"
            "<code>/whitelist remove user_id</code>\n"
            "<code>/whitelist list</code>"
        )
    
    action = m.command[1].lower()
    if action == "list":
        wl = await get_group_setting(0, "whitelist", [])
        await m.reply_text(f"<b>Whitelisted Users:</b>\n<code>{wl}</code>")
    elif action in ["add", "remove"]:
        if len(m.command) < 3:
            return await m.reply_text("❌ User ID required.")
        uid = int(m.command[2])
        wl = await get_group_setting(0, "whitelist", [])
        if action == "add" and uid not in wl:
            wl.append(uid)
        elif action == "remove" and uid in wl:
            wl.remove(uid)
        await set_group_setting(0, "whitelist", wl)
        await m.reply_text(f"✅ User <code>{uid}</code> {action}ed to whitelist.")
