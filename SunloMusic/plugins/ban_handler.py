import asyncio
from pyrogram import filters, enums
from pyrogram.types import CallbackQuery, Message
from SunloMusic.bot import bot, assistant, ensure_assistant_in_chat
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

# ✅ RENAMED: /unbanassistant (Normal /unban won't conflict now)
@bot.on_message(filters.command("unbanassistant") & filters.group)
@catch_errors
async def unban_assistant_cmd(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if not assistant:
        return await message.reply_text("❌ Assistant not initialized!")
        
    is_admin = False
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.privileges and (getattr(member.privileges, "can_restrict_members", False) or member.privileges.can_manage_chat):
            is_admin = True
    except: pass
    
    if not is_admin:
        return await message.reply_text("🚫 <b>Sirf Admins hi Assistant ko unban kar sakte hain!</b>")
    
    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        can_unban = bot_member.privileges and getattr(bot_member.privileges, "can_restrict_members", False)
    except: can_unban = False
    
    if not can_unban:
        return await message.reply_text("❌ <b>Mujhe permission nahi hai!</b>\n\nPlease promote me as Admin with <b>'Ban Users'</b> permission.")
    
    status = await message.reply_text("🔓 <b>Unbanning Assistant...</b>")
    
    try:
        await client.unban_chat_member(chat_id, assistant.me.id)
        await asyncio.sleep(2)
        add_status = await ensure_assistant_in_chat(chat_id)
        
        if add_status == "ok":
            await status.edit_text("✅ <b>Assistant Unbanned & Re-added!</b>")
        elif add_status == "failed_no_admin":
            await status.edit_text("✅ <b>Assistant Unbanned!</b>\n⚠️ But I need <b>'Invite Users'</b> permission to add the assistant back.")
        else:
            await status.edit_text(f"✅ <b>Assistant Unbanned!</b>\nPlease manually add <code>@{assistant.me.username}</code> back to the group.")
    except Exception as e:
        LOGGER.error(f"Unban assistant error: {e}")
        await status.edit_text(f"❌ <b>Failed:</b> <code>{e}</code>")

@bot.on_callback_query(filters.regex("^unban_assistant$"))
@catch_errors
async def unban_assistant_cb(client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    is_admin = False
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.privileges and (getattr(member.privileges, "can_restrict_members", False) or member.privileges.can_manage_chat): is_admin = True
    except: pass
    if not is_admin: return await callback.answer("🚫 Sirf Admins hi unban kar sakte hain!", show_alert=True)
    
    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        can_unban = bot_member.privileges and getattr(bot_member.privileges, "can_restrict_members", False)
    except: can_unban = False
    if not can_unban: return await callback.answer("❌ Mujhe 'Ban Users' permission nahi hai!", show_alert=True)
    
    if not assistant: return await callback.answer("❌ Assistant not initialized!", show_alert=True)
    
    try:
        await callback.answer("🔓 Unbanning...", show_alert=False)
        await client.unban_chat_member(chat_id, assistant.me.id)
        await asyncio.sleep(2)
        status = await ensure_assistant_in_chat(chat_id)
        
        if status == "ok":
            await callback.message.edit_text("✅ <b>Assistant Unbanned & Re-added!</b>")
        else:
            await callback.message.edit_text(f"✅ <b>Assistant Unbanned!</b>\nPlease manually add <code>@{assistant.me.username}</code> back.")
    except Exception as e:
        await callback.answer(f"❌ Failed: {e}", show_alert=True)

@bot.on_callback_query(filters.regex("^dismiss_ban$"))
@catch_errors
async def dismiss_ban_cb(client, callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Dismissed")
