from pyrogram import filters
from pyrogram.types import ChatJoinRequest
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

@bot.on_chat_join_request()
@catch_errors
async def join_request_handler(_, request: ChatJoinRequest):
    try:
        await request.approve()
        LOGGER.info(f"✅ Auto-approved join request for {request.from_user.id}")
        try:
            await bot.send_message(
                request.from_user.id, 
                f"✅ Your request to join <b>{request.chat.title}</b> has been approved!\nUse /help to see commands."
            )
        except: pass
    except Exception as e:
        LOGGER.error(f"Failed to approve: {e}")
