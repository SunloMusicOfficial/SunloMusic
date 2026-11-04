import asyncio, time, platform, os, sys, subprocess
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.database import set_auth, get_all_chats, get_stats, add_sudo, remove_sudo, sudo_col, is_sudo
from SunloMusic.decorators import sudo_only, admin_only, catch_errors
from SunloMusic.queues import active_chats, get_queue

@bot.on_message(filters.command("auth") & filters.group)
@catch_errors
@admin_only
async def auth_cmd(_, m: Message):
    await set_auth(m.chat.id, True)
    await m.reply_text("✅ <b>Chat Authorized</b>")

@bot.on_message(filters.command("stats"))
@catch_errors
@sudo_only
async def stats_cmd(_, m: Message):
    s = await get_stats()
    text = (
        f"📊 <b>SunloMusic Premium Stats</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{s['users']}</code>\n"
        f"💬 <b>Total Chats:</b> <code>{s['chats']}</code>\n"
        f"🎵 <b>Active VCs:</b> <code>{len(active_chats())}</code>\n"
        f"💻 <b>System:</b> <code>Python {platform.python_version()}</code>\n"
        f"━━━━━━━━━━━━━"
    )
    await m.reply_text(text)

# ✅ NEW: Set Bot Profile Photo (Bot API 9.4)
@bot.on_message(filters.command("setprofilepic"))
@catch_errors
@sudo_only
async def setprofilepic_cmd(_, m: Message):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply_text("❌ <b>Reply to a photo to set as bot profile pic.</b>")
    
    status = await m.reply_text("📸 <b>Setting profile picture...</b>")
    try:
        photo = await m.reply_to_message.download()
        await bot.set_profile_photo(photo=photo)
        await status.edit_text("✅ <b>Profile picture updated!</b>")
    except Exception as e:
        await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")

@bot.on_message(filters.command("broadcast"))
@catch_errors
@sudo_only
async def bc_cmd(_, m: Message):
    if not m.reply_to_message: return await m.reply_text("Reply to a message.")
    chats = await get_all_chats()
    status = await m.reply_text(f"📢 Broadcasting to {len(chats)} chats...")
    for c in chats:
        try: await m.reply_to_message.copy(c)
        except: pass
        await asyncio.sleep(0.1)
    await status.edit_text("✅ <b>Broadcast Complete</b>")

@bot.on_message(filters.command("addsudo"))
@catch_errors
@sudo_only
async def addsudo_cmd(_, m: Message):
    if not m.reply_to_message: return await m.reply_text("Reply to a user.")
    await add_sudo(m.reply_to_message.from_user.id)
    await m.reply_text("✅ <b>Sudo added.</b>")

@bot.on_message(filters.command("delsudo"))
@catch_errors
@sudo_only
async def delsudo_cmd(_, m: Message):
    if len(m.command) < 2: return await m.reply_text("Usage: /delsudo user_id")
    try:
        await remove_sudo(int(m.command[1]))
        await m.reply_text("🗑 <b>Sudo removed.</b>")
    except ValueError:
        await m.reply_text("❌ Invalid ID")

@bot.on_message(filters.command("sudolist"))
@catch_errors
@sudo_only
async def sudolist_cmd(_, m: Message):
    sudos = [u async for u in sudo_col.find({})]
    text = "<b>👑 Sudo Users List</b>\n━━━━━━━━━━━━━\n"
    if not sudos:
        text += "No sudo users found.\n"
    else:
        for idx, u in enumerate(sudos, 1):
            text += f"{idx}. <code>{u['user_id']}</code>\n"
    text += "━━━━━━━━━━━━━\n"
    text += f"<b>Owner:</b> <code>{config.OWNER_ID}</code>"
    await m.reply_text(text)
