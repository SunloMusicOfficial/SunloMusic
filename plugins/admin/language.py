from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import is_admin
from database.mongodb import db

@Client.on_message(filters.command("lang") & filters.group)
async def lang_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Admin rights required!")
        
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="setlang_hi"),
         InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en")]
    ])
    await message.reply_text("🌐 **Select Group Language:**", reply_markup=buttons)

@Client.on_callback_query(filters.regex("^setlang_"))
async def setlang_cb(client, cq):
    lang_code = cq.data.split("_")[1]
    # Update DB logic mapping here
    await db.groups.update_one({"chat_id": cq.message.chat.id}, {"$set": {"lang": lang_code}}, upsert=True)
    lang_name = "Hindi" if lang_code == "hi" else "English"
    await cq.message.edit_text(f"✅ **Language changed to {lang_name}!**")
