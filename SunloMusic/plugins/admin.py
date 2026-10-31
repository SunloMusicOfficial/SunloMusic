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

# ✅ ADVANCED STATS
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
        f"⏱ <b>Server Time:</b> <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"<i>Bot is running smoothly.</i>"
    )
    await m.reply_text(text)

# ✅ BROADCAST
@bot.on_message(filters.command("broadcast"))
@catch_errors
@sudo_only
async def bc_cmd(_, m: Message):
    if not m.reply_to_message: 
        return await m.reply_text("❌ <b>Reply to a message to broadcast.</b>")
    chats = await get_all_chats()
    status = await m.reply_text(f"📢 Broadcasting to {len(chats)} chats...")
    success, failed = 0, 0
    for c in chats:
        try: 
            await m.reply_to_message.copy(c)
            success += 1
        except: 
            failed += 1
        await asyncio.sleep(0.1)
    await status.edit_text(f"✅ <b>Broadcast Complete</b>\n\n🟢 Success: {success}\n🔴 Failed: {failed}")

# ✅ SUDO MANAGEMENT (No filters.private)
@bot.on_message(filters.command("addsudo"))
@catch_errors
@sudo_only
async def addsudo_cmd(_, m: Message):
    if not m.reply_to_message: 
        return await m.reply_text("❌ <b>Reply to a user to make them sudo.</b>")
    await add_sudo(m.reply_to_message.from_user.id)
    await m.reply_text("✅ <b>Sudo added.</b>")

@bot.on_message(filters.command("delsudo"))
@catch_errors
@sudo_only
async def delsudo_cmd(_, m: Message):
    if not m.reply_to_message and len(m.command) < 2: 
        return await m.reply_text("❌ <b>Reply to a user or provide ID.</b>")
    
    target = m.reply_to_message.from_user.id if m.reply_to_message else int(m.command[1])
    await remove_sudo(target)
    await m.reply_text("🗑 <b>Sudo removed.</b>")

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

# ✅ PREMIUM: ACTIVE VC TRACKER (No filters.private)
@bot.on_message(filters.command("activevc"))
@catch_errors
@sudo_only
async def activevc_cmd(_, m: Message):
    chats = active_chats()
    if not chats:
        return await m.reply_text("📭 <b>No active Voice Chats right now.</b>")
    
    text = "<b>🎵 Active Voice Chats</b>\n━━━━━━━━━━━━━\n"
    for c in chats:
        q = get_queue(c)
        if q.now_playing:
            text += f"💬 <code>{c}</code>\n🎶 <i>{q.now_playing.title[:30]}</i>\n\n"
        else:
            text += f"💬 <code>{c}</code>\n🎶 <i>Connecting...</i>\n\n"
    text += f"<b>Total:</b> {len(chats)}"
    await m.reply_text(text)

# ✅ PREMIUM: EVAL (No filters.private)
@bot.on_message(filters.command("eval"))
@catch_errors
@sudo_only
async def eval_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/eval print('hello')</code>")
    code = m.text.split(None, 1)[1]
    try:
        result = eval(code)
        if asyncio.iscoroutine(result):
            result = await result
        await m.reply_text(f"✅ <b>Result:</b>\n<code>{result}</code>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b>\n<code>{e}</code>")

# ✅ PREMIUM: SHELL COMMAND (No filters.private)
@bot.on_message(filters.command("sh"))
@catch_errors
@sudo_only
async def sh_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/sh ls -la</code>")
    cmd = m.text.split(None, 1)[1]
    try:
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        out = (stdout.decode() + stderr.decode()).strip()
        if not out: out = "No output."
        if len(out) > 4000: out = out[:4000] + "\n...(truncated)"
        await m.reply_text(f"✅ <b>Output:</b>\n<pre>{out}</pre>")
    except Exception as e:
        await m.reply_text(f"❌ <b>Error:</b>\n<code>{e}</code>")

# ✅ PREMIUM: RESTART BOT (No filters.private)
@bot.on_message(filters.command("restart"))
@catch_errors
@sudo_only
async def restart_cmd(_, m: Message):
    await m.reply_text("🔄 <b>Restarting SunloMusic...</b>")
    await asyncio.sleep(2)
    os.execl(sys.executable, sys.executable, *sys.argv)
