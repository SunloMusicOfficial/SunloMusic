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
        f"⏱ <b>Server Time:</b> <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"<i>Bot is running smoothly.</i>"
    )
    await m.reply_text(text)

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

# ✅ PREMIUM ACTIVE VC TRACKER (With Auto Links & Dashboard)
@bot.on_message(filters.command("activevc"))
@catch_errors
@sudo_only
async def activevc_cmd(_, m: Message):
    chats = active_chats()
    if not chats:
        return await m.reply_text("📭 <b>No active Voice Chats right now.</b>")
    
    status = await m.reply_text("📡 <i>Scanning active Voice Chats...</i>")
    
    text = "⚡ <b>『 ACTIVE VC MONITOR 』</b> ⚡\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
    
    for c in chats:
        q = get_queue(c)
        try:
            chat = await bot.get_chat(c)
            chat_title = chat.title or "Private Group"
            
            # ✅ Smart Link Generation
            if chat.username:
                link = f"https://t.me/{chat.username}"
                link_text = f"<a href='{link}'>🔗 Click Here</a>"
            else:
                try:
                    invite = await bot.export_chat_invite_link(c)
                    link_text = f"<a href='{invite}'>🔗 Join Link</a>"
                except:
                    link_text = "<i>No Public Link</i>"
                    
        except:
            chat_title = "Unknown Group"
            link_text = "<i>No Link Available</i>"

        if q.now_playing:
            song = q.now_playing.title[:30] + ("..." if len(q.now_playing.title) > 30 else "")
            req = q.now_playing.requester
            text += (
                f"🎧 <b>Group:</b> {chat_title}\n"
                f"{link_text}\n"
                f"🆔 <b>ID:</b> <code>{c}</code>\n"
                f"▶️ <b>Playing:</b> <i>{song}</i>\n"
                f"🙋‍♂️ <b>By:</b> {req}\n"
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            )
        else:
            text += (
                f"🎧 <b>Group:</b> {chat_title}\n"
                f"{link_text}\n"
                f"🆔 <b>ID:</b> <code>{c}</code>\n"
                f"⏳ <b>Status:</b> <i>Connecting...</i>\n"
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            )
            
    text += f"🌐 <b>Total Active VCs:</b> <code>{len(chats)}</code>"
    
    await status.delete()
    await m.reply_text(text, disable_web_page_preview=True)
