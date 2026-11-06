import asyncio
from pyrogram import filters, enums
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot, assistant, ensure_assistant_in_chat
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

@bot.on_callback_query(filters.regex("^unban_assistant$"))
@catch_errors
async def unban_assistant_cb(client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    # 1. Check if user is admin
    is_admin = False
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.privileges and (getattr(member.privileges, "can_restrict_members", False) or member.privileges.can_manage_chat):
            is_admin = True
    except: pass
    
    if not is_admin:
        return await callback.answer("🚫 Sirf Admins hi Assistant ko unban kar sakte hain!", show_alert=True)
    
    # 2. Check if bot has permission to unban
    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        can_unban = bot_member.privileges and getattr(bot_member.privileges, "can_restrict_members", False)
    except: can_unban = False
    
    if not can_unban:
        return await callback.answer(
            "❌ Mujhe permission nahi hai!\n\n"
            "Please promote me as Admin with 'Ban Users' permission.",
            show_alert=True
        )
    
    if not assistant:
        return await callback.answer("❌ Assistant not initialized!", show_alert=True)
    
    # 3. Unban Assistant
    try:
        await callback.answer("🔓 Unbanning...", show_alert=False)
        await client.unban_chat_member(chat_id, assistant.me.id)
        
        # 4. Try to re-add
        await asyncio.sleep(2)
        status = await ensure_assistant_in_chat(chat_id)
        
        if status == "ok":
            await callback.message.edit_text(
                "✅ <b>Assistant Unbanned & Re-added!</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Voice Chat is ready again. Use /play to start music!"
            )
        elif status == "failed_no_admin":
            await callback.message.edit_text(
                "✅ <b>Assistant Unbanned!</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "⚠️ But I need <b>'Invite Users'</b> permission to add the assistant back.\n"
                "Please add the assistant manually or grant me that permission."
            )
        else:
            await callback.message.edit_text(
                "✅ <b>Assistant Unbanned!</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"Please manually add <code>@{assistant.me.username}</code> back to the group."
            )
    except Exception as e:
        LOGGER.error(f"Unban error: {e}")
        await callback.answer(f"❌ Failed: {e}", show_alert=True)

@bot.on_callback_query(filters.regex("^dismiss_ban$"))
@catch_errors
async def dismiss_ban_cb(client, callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Dismissed")
