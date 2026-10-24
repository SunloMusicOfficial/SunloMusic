from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.vars import Config

# Apna channel username yahan set karein (e.g., "SunloMusicOfficial")
FSUB_CHANNEL = "SunloMusicOfficial" 

async def check_fsub(client, message):
    if not FSUB_CHANNEL: return True
    try:
        await client.get_chat_member(FSUB_CHANNEL, message.from_user.id)
        return True
    except UserNotParticipant:
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL}")]])
        await message.reply_text(
            "⚠️ **Must Join Channel!**\n\nAapko music play karne se pehle humara official channel join karna hoga.",
            reply_markup=buttons
        )
        return False
    except:
        return True
