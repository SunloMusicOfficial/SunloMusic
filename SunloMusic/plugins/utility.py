from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import set_afk, get_afk, remove_afk, get_leaderboard
from SunloMusic.queues import get_queue

@bot.on_message(filters.command("afk") & filters.group)
@catch_errors
async def afk_cmd(_, m: Message):
    reason = " ".join(m.command[1:]) if len(m.command) > 1 else "No reason provided."
    await set_afk(m.from_user.id, reason)
    await m.reply_text(f"💤 <b>{m.from_user.first_name} is now AFK.</b>\n📝 <b>Reason:</b> {reason}")

@bot.on_message(filters.group, group=10)
@catch_errors
async def check_afk(_, m: Message):
    if not m.from_user or m.from_user.is_bot: return
    afk_reason = await get_afk(m.from_user.id)
    if afk_reason:
        await remove_afk(m.from_user.id)
        return await m.reply_text(f"👋 <b>Welcome back {m.from_user.first_name}!</b> I removed your AFK status.")
        
    if m.reply_to_message and m.reply_to_message.from_user:
        target_afk = await get_afk(m.reply_to_message.from_user.id)
        if target_afk:
            return await m.reply_text(f"💤 <b>{m.reply_to_message.from_user.first_name} is currently AFK.</b>\n📝 <b>Reason:</b> {target_afk}")

@bot.on_message(filters.command("leaderboard") & filters.group)
@catch_errors
async def lb_cmd(_, m: Message):
    top_users = await get_leaderboard(m.chat.id, limit=5)
    if not top_users:
        return await m.reply_text("📊 <b>Leaderboard is empty!</b>\nStart playing songs to earn points.")
        
    text = "<b>🏆 Group Leaderboard 🏆</b>\n━━━━━━━━━━━━━\n"
    for i, user in enumerate(top_users, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{emoji} <a href='tg://user?id={user['user_id']}'>{user['name']}</a> - <code>{user['points']}</code> plays\n"
    text += "━━━━━━━━━━━━━"
    await m.reply_text(text)

# ✅ PREMIUM GSTATS
@bot.on_message(filters.command("gstats") & filters.group)
@catch_errors
async def gstats_cmd(_, m: Message):
    status_msg = await m.reply_text("⏳ <b>Fetching Premium Stats...</b>")
    
    # Get Chat Data (Fix for "None" members)
    try:
        chat = await bot.get_chat(m.chat.id)
        member_count = chat.members_count or "N/A"
        chat_photo = chat.photo.big_file_id if chat.photo else None
    except:
        member_count = "N/A"
        chat_photo = None

    # Get VC Status
    q = get_queue(m.chat.id)
    if q.now_playing:
        vc_status = f"▶️ <i>{q.now_playing.title[:25]}...</i>"
    else:
        vc_status = "💤 <i>No active stream</i>"

    # Get Top 3 Leaderboard
    top_users = await get_leaderboard(m.chat.id, limit=3)
    lb_text = ""
    if top_users:
        for i, user in enumerate(top_users, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            lb_text += f"{emoji} <a href='tg://user?id={user['user_id']}'>{user['name']}</a> - <code>{user['points']}</code>\n"
    else:
        lb_text = "<i>No plays yet</i>\n"

    text = (
        f"⚡ <b>『 PREMIUM DASHBOARD 』</b> ⚡\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🏷 <b>Group:</b> {chat.title if chat else m.chat.title}\n"
        f"🆔 <b>ID:</b> <code>{m.chat.id}</code>\n"
        f"👥 <b>Members:</b> <code>{member_count}</code>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🎧 <b>VC Status:</b> {vc_status}\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🏆 <b>Top 3 Listeners:</b>\n"
        f"{lb_text}"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👑 <b>Powered by:</b> <a href='https://t.me/YO_UR_OFFICIAL_CRUSH'>Sakil</a>"
    )

    await status_msg.delete()
    
    # Try sending with Group Photo
    if chat_photo:
        try:
            await m.reply_photo(chat_photo, caption=text)
            return
        except:
            pass
            
    await m.reply_text(text)
