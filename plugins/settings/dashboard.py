from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.mongodb import db
from utils.decorators import is_admin

def get_settings_keyboard(strict_mode: bool):
    strict_text = "✅ ON" if strict_mode else "❌ OFF"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Strict Mode: {strict_text}", callback_data="toggle_strict")
        ],
        [
            InlineKeyboardButton("🗑 Close Panel", callback_data="close_panel")
        ]
    ])

@Client.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **You must be an Admin to open Settings!**")
        
    group_data = await db.get_group(message.chat.id)
    strict_mode = group_data.get("strict_mode", False)
    
    await message.reply_text(
        "⚙️ **SunloMusic Group Settings**\n\n"
        "Configure bot behavior for your group here:",
        reply_markup=get_settings_keyboard(strict_mode)
    )

@Client.on_callback_query(filters.regex("^toggle_strict$"))
async def toggle_strict_cb(client: Client, cq: CallbackQuery):
    if not await is_admin(client, cq.message.chat.id, cq.from_user.id):
        return await cq.answer("Only admins can change settings!", show_alert=True)
        
    new_status = await db.toggle_strict_mode(cq.message.chat.id)
    await cq.message.edit_reply_markup(reply_markup=get_settings_keyboard(new_status))
    await cq.answer(f"Strict Mode is now {'ON' if new_status else 'OFF'}!", show_alert=True)

@Client.on_callback_query(filters.regex("^close_panel$"))
async def close_panel_cb(client: Client, cq: CallbackQuery):
    if not await is_admin(client, cq.message.chat.id, cq.from_user.id):
        return await cq.answer("Only admins can close this!", show_alert=True)
    await cq.message.delete()
