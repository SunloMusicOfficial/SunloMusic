from pyrogram import Client, filters
from pyrogram.types import Message
from config.vars import Config
from core.call import sunlo_call

@Client.on_message(filters.command("setname") & filters.user(Config.OWNER_ID))
async def set_name_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
    
    new_name = message.text.split(None, 1)[1]
    try:
        # Assuming sunlo_call has access to the assistant client
        assistant = sunlo_call._app # Replace with actual assistant client variable
        await assistant.update_profile(first_name=new_name)
        await message.reply_text(f"✅ **Assistant Name Updated to:** {new_name}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@Client.on_message(filters.command("setbio") & filters.user(Config.OWNER_ID))
async def set_bio_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
    
    new_bio = message.text.split(None, 1)[1]
    try:
        assistant = sunlo_call._app
        await assistant.update_profile(bio=new_bio)
        await message.reply_text(f"✅ **Assistant Bio Updated!**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@Client.on_message(filters.command("setpfp") & filters.user(Config.OWNER_ID))
async def set_pfp_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("⚠️ **Reply to a photo with  to update Assistant's Profile Picture.**")
    
    status = await message.reply_text("🔄 **Downloading photo...**")
    try:
        photo_path = await message.reply_to_message.download()
        assistant = sunlo_call._app
        await assistant.set_profile_photo(photo=photo_path)
        await status.edit_text("✅ **Assistant Profile Picture Updated!**")
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")
