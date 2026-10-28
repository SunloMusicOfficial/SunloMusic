import asyncio, time, platform
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.database import set_auth, get_all_chats, get_stats, add_sudo, remove_sudo
from SunloMusic.decorators import sudo_only, admin_only, catch_errors
from SunloMusic.queues import active_chats

@bot.on_message(filters.command("auth") & filters.group)
@catch_errors
@admin_only
async def auth_cmd(_, m):
    await set_auth(m.chat.id, True)
    await m.reply_text("✅ <b>Chat Authorized</b>")

@bot.on_message(filters.command("stats"))
@catch_errors
@sudo_only
async def stats_cmd(_, m):
    s = await get_stats()
    uptime = int(time.time() - m.date.timestamp()) # Simplified uptime
    text = (
        f"📊 <b>SunloMusic Premium Stats</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{s['users']}</code>\n"
        f"💬 <b>Total Chats:</b> <code>{s['chats']}</code>\n"
        f"🎵 <b>Active VCs:</b> <code>{len(active_chats())}</code>\n"
        f"💻 <b>System:</b> <code>Python {platform.python_version()}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"<i>Bot is running smoothly.</i>"
    )
    await m.reply_text(text)

@bot.on_message(filters.command("broadcast"))
@catch_errors
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

@bot.on_message(filters.command("addsudo") & filters.private)
@catch_errors
@sudo_only
async def addsudo_cmd(_, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a user.")
    await add_sudo(m.reply_to_message.from_user.id)
    await m.reply_text("✅ <b>Sudo added.</b>")

@bot.on_message(filters.command("delsudo") & filters.private)
@catch_errors
@sudo_only
async def delsudo_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <code>/delsudo user_id</code>")
    try:
        await remove_sudo(int(m.command[1]))
        await m.reply_text("🗑 <b>Sudo removed.</b>")
    except ValueError:
        await m.reply_text("❌ Invalid ID")
