import asyncio
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.database import set_auth, get_all_chats, get_stats, add_sudo, remove_sudo
from SunloMusic.decorators import catch_errors, sudo_only, admin_only

@catch_errors
@bot.on_message(filters.command("auth") & filters.group)
@admin_only
async def auth_cmd(_, m):
    await set_auth(m.chat.id, True)
    await m.reply_text("✅ <b>Chat Authorized</b>")

@catch_errors
@bot.on_message(filters.command("stats"))
@sudo_only
async def stats_cmd(_, m):
    s = await get_stats()
    await m.reply_text(f"📊 <b>Stats</b>\n\n👥 Users: <code>{s['users']}</code>\n💬 Chats: <code>{s['chats']}</code>")

@catch_errors
@bot.on_message(filters.command("broadcast"))
@sudo_only
async def bc_cmd(_, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a message.")
    chats = await get_all_chats()
    status = await m.reply_text(f"📢 Broadcasting to {len(chats)} chats...")
    for c in chats:
        try: await m.reply_to_message.copy(c)
        except: pass
        await asyncio.sleep(0.1)
    await status.edit_text("✅ <b>Broadcast Complete</b>")

@catch_errors
@bot.on_message(filters.command("addsudo") & filters.private)
@sudo_only
async def addsudo_cmd(_, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a user.")
    await add_sudo(m.reply_to_message.from_user.id)
    await m.reply_text("✅ <b>Sudo added.</b>")

@catch_errors
@bot.on_message(filters.command("delsudo") & filters.private)
@sudo_only
async def delsudo_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <code>/delsudo user_id</code>")
    try:
        await remove_sudo(int(m.command[1]))
        await m.reply_text("🗑 <b>Sudo removed.</b>")
    except ValueError:
        await m.reply_text("❌ Invalid ID")
