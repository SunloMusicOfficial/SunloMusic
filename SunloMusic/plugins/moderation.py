import asyncio, random
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import set_group_setting, get_group_setting
from SunloMusic.logger import LOGGER

EMOJIS = ["🍃", "🌿", "🌺", "🌸", "🦋", "✨", "💎", "🪐", "🌌", "🔥", "🎵", "🎶", "🌟", "👑", "🥂", "🎧", "⚜️"]

# ✅ Anti-Link & Anti-Forward Handler
@bot.on_message(filters.group & ~filters.service & ~filters.bot, group=15)
@catch_errors
async def moderation_handler(_, m: Message):
    if not m.text and not m.caption: return
    
    is_admin = False
    try:
        member = await m.chat.get_member(m.from_user.id)
        if member.privileges and (member.privileges.can_manage_chat or member.privileges.can_delete_messages): 
            is_admin = True
    except: pass
    
    if is_admin: return

    # 1. Anti-Link Check
    is_antilink = await get_group_setting(m.chat.id, "antilink", False)
    if is_antilink:
        has_link = False
        if m.entities:
            for e in m.entities:
                if e.type in (enums.MessageEntityType.URL, enums.MessageEntityType.TEXT_LINK): has_link = True
        if m.caption_entities:
            for e in m.caption_entities:
                if e.type in (enums.MessageEntityType.URL, enums.MessageEntityType.TEXT_LINK): has_link = True
                
        if has_link:
            try:
                await m.delete()
                await m.reply_text(f"⚠️ {m.from_user.mention}, <b>Links are not allowed here!</b>")
                return
            except: pass

    # 2. Anti-Forward Check
    is_antiforward = await get_group_setting(m.chat.id, "antiforward", False)
    if is_antiforward:
        if m.forward_date or getattr(m, "forward_from", None) or getattr(m, "forward_from_chat", None):
            try:
                await m.delete()
                await m.reply_text(f"⚠️ {m.from_user.mention}, <b>Forwarded messages are not allowed here!</b>")
                return
            except: pass

@bot.on_message(filters.command("antilink") & filters.group)
@catch_errors
async def antilink_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/antilink on</code> or <code>/antilink off</code>")
    state = m.command[1].lower()
    await set_group_setting(m.chat.id, "antilink", state == "on")
    await m.reply_text(f"✅ <b>Anti-Link {state.upper()}!</b>")

@bot.on_message(filters.command("antiforward") & filters.group)
@catch_errors
async def antiforward_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/antiforward on</code> or <code>/antiforward off</code>")
    state = m.command[1].lower()
    await set_group_setting(m.chat.id, "antiforward", state == "on")
    await m.reply_text(f"✅ <b>Anti-Forward {state.upper()}!</b>")

# ✅ Captcha System
@bot.on_message(filters.new_chat_members)
@catch_errors
async def captcha_handler(_, m: Message):
    is_captcha = await get_group_setting(m.chat.id, "captcha", False)
    if not is_captcha: return
    
    for user in m.new_chat_members:
        if user.is_bot: continue
        try:
            await bot.restrict_chat_member(m.chat.id, user.id, enums.ChatPermissions())
            emoji = random.choice(EMOJIS)
            btn1 = InlineKeyboardButton(emoji, callback_data=f"captcha_{user.id}_{emoji}")
            btn2 = InlineKeyboardButton("🚫", callback_data=f"captcha_{user.id}_wrong")
            btn3 = InlineKeyboardButton("✅", callback_data=f"captcha_{user.id}_wrong")
            
            await m.reply_text(
                f"🛡️ <b>Verification Required!</b>\n\n"
                f"Welcome {user.mention}.\n"
                f"Please click on the <b>{emoji}</b> emoji to verify you are human.",
                reply_markup=InlineKeyboardMarkup([[btn2, btn1, btn3]])
            )
        except Exception as e:
            LOGGER.error(f"Captcha Error: {e}")

@bot.on_callback_query(filters.regex("^captcha_"))
@catch_errors
async def captcha_cb(_, cq):
    _, user_id, correct_emoji = cq.data.split("_")
    if cq.from_user.id != int(user_id):
        return await cq.answer("This is not your captcha!", show_alert=True)
        
    if correct_emoji == "wrong":
        return await cq.answer("❌ Incorrect! Try again.", show_alert=True)
        
    try:
        await bot.restrict_chat_member(
            cq.message.chat.id, cq.from_user.id, 
            enums.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        )
        await cq.message.delete()
        await bot.send_message(cq.message.chat.id, f"✅ {cq.from_user.mention} verified successfully!")
    except Exception as e:
        LOGGER.error(f"Unrestrict error: {e}")

@bot.on_message(filters.command("captcha") & filters.group)
@catch_errors
async def captcha_toggle_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/captcha on</code> or <code>/captcha off</code>")
    state = m.command[1].lower()
    await set_group_setting(m.chat.id, "captcha", state == "on")
    await m.reply_text(f"✅ <b>Captcha Verification {state.upper()}!</b>")
