from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import set_afk, get_afk, remove_afk, get_leaderboard

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
    
    # Check if the sender is back
    afk_reason = await get_afk(m.from_user.id)
    if afk_reason:
        await remove_afk(m.from_user.id)
        return await m.reply_text(f"👋 <b>Welcome back {m.from_user.first_name}!</b> I removed your AFK status.")
        
    # Check if someone tagged an AFK user
    if m.reply_to_message and m.reply_to_message.from_user:
        target_afk = await get_afk(m.reply_to_message.from_user.id)
        if target_afk:
            return await m.reply_text(f"💤 <b>{m.reply_to_message.from_user.first_name} is currently AFK.</b>\n📝 <b>Reason:</b> {target_afk}")
            
    if m.entities:
        for entity in m.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                username = m.text[entity.offset:entity.offset + entity.length].replace("@", "")
                # Note: To check by username properly we would need to resolve it to ID, 
                # but for simplicity, we just check if the username matches.
                # For a full fix, resolving username to ID is needed. 
                pass

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

@bot.on_message(filters.command("gstats") & filters.group)
@catch_errors
async def gstats_cmd(_, m: Message):
    total_members = m.chat.members_count if hasattr(m.chat, 'members_count') else "N/A"
    text = (
        f"<b>📊 {m.chat.title} Stats</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🆔 <b>Chat ID:</b> <code>{m.chat.id}</code>\n"
        f"👥 <b>Total Members:</b> {total_members}\n"
        f"📝 <b>Type:</b> Supergroup\n"
        f"━━━━━━━━━━━━━"
    )
    await m.reply_text(text)
