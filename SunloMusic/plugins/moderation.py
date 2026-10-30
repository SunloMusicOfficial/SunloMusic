import asyncio
import random
from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import set_group_setting, get_group_setting
from SunloMusic.logger import LOGGER

# ✅ Random Premium Emojis List
EMOJIS = ["🍃", "🌿", "🌺", "🌸", "🦋", "✨", "💎", "🪐", "🌌", "🔥", "🎵", "🎶", "🌟", "👑", "🥂", "🎧", "⚜️"]

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

    # Reply message copy karega agar diya gaya ho
    if m.reply_to_message:
        try: await m.reply_to_message.copy(m.chat.id)
        except: pass

    # ✅ Header (Option 9 + Aesthetic Style)
    header = (
        f"✨ ─── 𝓐𝓽𝓽𝓮𝓷𝓽𝓲𝓸𝓷 ─── ✨\n\n"
        f"🌸 <i>{custom_msg if custom_msg else 'Please read the above message.'}</i>\n\n"
        f"🕊️ <b>With regards,</b> {m.from_user.mention}\n"
        f"━━━━━━━━━━━━━\n"
        f"🔔 <b>Notifications:</b>\n\n"
    )

    current_text = header
    count = 0
    
    async for member in m.chat.get_members():
        if member.user.is_bot or member.user.is_deleted:
            continue
            
        # ✅ Har user ke liye random emoji select karega
        emoji = random.choice(EMOJIS)
        line = f"{emoji} {member.user.mention}\n"
        
        # Telegram limit check (3900 chars to be safe)
        if len(current_text) + len(line) > 3900:
            try: 
                await bot.send_message(m.chat.id, current_text, disable_notification=(count > 0))
            except Exception as e: 
                LOGGER.error(f"Tagall send error: {e}")
            # Naya message start
            current_text = line
            count += 1
            await asyncio.sleep(1) # Delay to prevent flood
        else:
            current_text += line

    # Last chunk send
    if current_text:
        try: 
            await bot.send_message(m.chat.id, current_text, disable_notification=(count > 0))
        except Exception as e: 
            LOGGER.error(f"Tagall final error: {e}")

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
