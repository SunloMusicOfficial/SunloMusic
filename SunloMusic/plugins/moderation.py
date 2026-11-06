import asyncio, random
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.database import set_group_setting, get_group_setting
from SunloMusic.logger import LOGGER

EMOJIS = ["🍃", "🌿", "🌺", "🌸", "🦋", "✨", "💎", "🪐", "🌌", "🔥", "🎵", "🎶", "🌟", "👑", "🥂", "🎧", "⚜️"]

# ═══════════════════════════════════════════
# ✅ NEW: BAN / UNBAN / MUTE / UNMUTE COMMANDS
# ═══════════════════════════════════════════

async def _extract_target(m: Message):
    """Extracts user ID from reply or command argument"""
    if m.reply_to_message and m.reply_to_message.from_user:
        return m.reply_to_message.from_user.id, m.reply_to_message.from_user.mention
    if len(m.command) > 1:
        try:
            uid = int(m.command[1])
            return uid, f"<code>{uid}</code>"
        except ValueError:
            return None, None
    return None, None

@bot.on_message(filters.command("ban") & filters.group)
@catch_errors
@admin_only
async def ban_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    target_id, target_name = await _extract_target(m)
    if not target_id: return await m.reply_text("❌ <b>Reply to a user or provide a valid ID.</b>")
    
    try:
        await bot.ban_chat_member(m.chat.id, target_id)
        await m.reply_text(f"🔨 <b>Banned:</b> {target_name}")
    except Exception as e:
        await m.reply_text(f"❌ <b>Failed to ban:</b> <code>{e}</code>")

@bot.on_message(filters.command("unban") & filters.group)
@catch_errors
@admin_only
async def unban_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    target_id, target_name = await _extract_target(m)
    if not target_id: return await m.reply_text("❌ <b>Reply to a user or provide a valid ID.</b>")
    
    try:
        await bot.unban_chat_member(m.chat.id, target_id)
        await m.reply_text(f"✅ <b>Unbanned:</b> {target_name}")
    except Exception as e:
        await m.reply_text(f"❌ <b>Failed to unban:</b> <code>{e}</code>")

@bot.on_message(filters.command("mute") & filters.group)
@catch_errors
@admin_only
async def mute_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    target_id, target_name = await _extract_target(m)
    if not target_id: return await m.reply_text("❌ <b>Reply to a user or provide a valid ID.</b>")
    
    try:
        await bot.restrict_chat_member(
            m.chat.id, target_id, 
            enums.ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
        )
        await m.reply_text(f"🔇 <b>Muted:</b> {target_name}")
    except Exception as e:
        await m.reply_text(f"❌ <b>Failed to mute:</b> <code>{e}</code>")

@bot.on_message(filters.command("unmute") & filters.group)
@catch_errors
@admin_only
async def unmute_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    target_id, target_name = await _extract_target(m)
    if not target_id: return await m.reply_text("❌ <b>Reply to a user or provide a valid ID.</b>")
    
    try:
        await bot.restrict_chat_member(
            m.chat.id, target_id, 
            enums.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        )
        await m.reply_text(f"🔊 <b>Unmuted:</b> {target_name}")
    except Exception as e:
        await m.reply_text(f"❌ <b>Failed to unmute:</b> <code>{e}</code>")


# ═══════════════════════════════════════════
# EXISTING MODERATION FEATURES
# ═══════════════════════════════════════════

@bot.on_message(filters.command("id") & filters.group)
@catch_errors
async def id_cmd(_, m: Message):
    if m.reply_to_message:
        user = m.reply_to_message.from_user
        text = f"👤 <b>User ID:</b> <code>{user.id}</code>\n📝 <b>Name:</b> {user.mention}\n💬 <b>Message ID:</b> <code>{m.reply_to_message.id}</code>"
    else:
        text = f"💬 <b>Chat ID:</b> <code>{m.chat.id}</code>\n👤 <b>Your ID:</b> <code>{m.from_user.id}</code>"
    await m.reply_text(text)

@bot.on_message(filters.command("purge") & filters.group)
@catch_errors
@admin_only
async def purge_cmd(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("❌ <b>Reply to a message to start purging from.</b>")
    start_id = m.reply_to_message.id
    end_id = m.id
    msg_ids = list(range(start_id, end_id + 1))
    for i in range(0, len(msg_ids), 100):
        try: await bot.delete_messages(m.chat.id, msg_ids[i:i+100])
        except: pass
    try: await m.reply_text(f"🧹 <b>Purged {len(msg_ids)} messages.</b>")
    except: pass

@bot.on_message(filters.command("tagall") & filters.group)
@catch_errors
@admin_only
async def tagall_cmd(_, m: Message):
    custom_msg = " ".join(m.command[1:]) if len(m.command) > 1 else None
    if not custom_msg and not m.reply_to_message:
        return await m.reply_text("❌ <b>Usage:</b> <code>/tagall [message]</code> or reply to a message.")

    status = await m.reply_text("⏳ <b>Preparing premium tags...</b>")
    try: await m.delete()
    except: pass

    if m.reply_to_message:
        try: await m.reply_to_message.copy(m.chat.id)
        except: pass

    msg_text = f"<blockquote><b>{custom_msg}</b></blockquote>" if custom_msg else ""
    header = f"✨ ─── 𝓐𝓽𝓽𝓮𝓷𝓽𝓲𝓸𝓷 ─── ✨\n\n🌸 {msg_text}\n\n🕊️ <b>With regards,</b> {m.from_user.mention}\n━━━━━━━━━━━━━\n🕊️ <b>Peaceful Pings:</b>\n\n"

    current_text = header
    count = 0
    member_count = 0 
    
    async for member in m.chat.get_members():
        if member.user.is_bot or member.user.is_deleted: continue
        emoji = random.choice(EMOJIS)
        line = f"{emoji} {member.user.mention}\n"
        current_text += line
        member_count += 1
        
        if member_count == 20:
            try: await bot.send_message(m.chat.id, current_text, disable_notification=(count > 0))
            except Exception as e: LOGGER.error(f"Tagall send error: {e}")
            current_text = "" 
            member_count = 0
            count += 1
            await asyncio.sleep(1) 

    if current_text:
        try: await bot.send_message(m.chat.id, current_text, disable_notification=(count > 0))
        except Exception as e: LOGGER.error(f"Tagall final error: {e}")

    await status.delete()

@bot.on_message(filters.command("welcome") & filters.group)
@catch_errors
@admin_only
async def welcome_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/welcome on</code> or <code>/welcome off</code>")
    state = m.command[1].lower()
    if state == "on":
        await set_group_setting(m.chat.id, "welcome", True)
        await m.reply_text("✅ <b>Welcome Messages Enabled!</b>")
    elif state == "off":
        await set_group_setting(m.chat.id, "welcome", False)
        await m.reply_text("❌ <b>Welcome Messages Disabled.</b>")

@bot.on_message(filters.new_chat_members)
@catch_errors
async def welcome_new_member(_, m: Message):
    is_welcome = await get_group_setting(m.chat.id, "welcome", False)
    if not is_welcome: return
    for user in m.new_chat_members:
        if user.is_bot: continue
        caption = (
            f"<b>✨ Welcome to {m.chat.title}!</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {user.mention}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"━━━━━━━━━━━━━\n"
            f"<i>Hope you enjoy your stay here. Use /play to listen to music!</i>"
        )
        try: await m.reply_text(caption)
        except: pass
