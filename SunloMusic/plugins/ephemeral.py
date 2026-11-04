from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

async def send_ephemeral(chat_id: int, user_id: int, text: str, reply_markup=None):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            ephemeral_message_parameters={"receiver_user_id": user_id}
        )
        return True
    except Exception as e:
        LOGGER.error(f"Ephemeral Send Error: {e}")
        return False

@bot.on_message(filters.command("afk") & filters.group)
@catch_errors
async def afk_cmd(_, m: Message):
    reason = " ".join(m.command[1:]) if len(m.command) > 1 else "No reason provided."
    from SunloMusic.database import set_afk
    await set_afk(m.from_user.id, reason)
    
    await send_ephemeral(
        m.chat.id, m.from_user.id,
        f"💤 <b>{m.from_user.first_name} is now AFK.</b>\n📝 <b>Reason:</b> {reason}",
    )

@bot.on_message(filters.command("daily") & filters.group)
@catch_errors
async def daily_cmd(_, m: Message):
    from SunloMusic.database import claim_daily, get_daily_cooldown, add_coins
    user_id = m.from_user.id
    result = await claim_daily(user_id)
    if result is None:
        remaining = await get_daily_cooldown(user_id)
        hrs, mins = remaining // 3600, (remaining % 3600) // 60
        return await send_ephemeral(m.chat.id, user_id, f"⏳ <b>Already claimed!</b>\nCome back in <code>{hrs}h {mins}m</code>")
    
    new_bal = await add_coins(user_id, 50)
    await send_ephemeral(m.chat.id, user_id, f"🎁 <b>+50 Coins!</b>\n💰 <b>Balance:</b> <code>{new_bal}</code>")
