import asyncio
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors

@bot.on_message(filters.command("ghost") & filters.group)
@catch_errors
async def ghost_cmd(_, m: Message):
    try:
        # Send ephemeral message
        msg = await bot.send_message(
            chat_id=m.chat.id,
            text="👻 This message will disappear and edit in 3 seconds...",
            ephemeral_message_parameters={"receiver_user_id": m.from_user.id}
        )
        
        await asyncio.sleep(3)
        
        # Edit the ephemeral message
        await bot.edit_ephemeral_message_text(
            chat_id=m.chat.id,
            message_id=msg.id,
            text="✨ <b>Surprise! I got edited.</b>",
            ephemeral_message_parameters={"receiver_user_id": m.from_user.id}
        )
    except Exception as e:
        await m.reply_text(f"Ephemeral not supported: {e}")

# Set Ephemeral Commands (BotCommand is_ephemeral)
@bot.on_message(filters.command("setephemeralcmds") & filters.private)
@catch_errors
async def set_ephemeral_cmds(_, m: Message):
    try:
        from pyrogram.types import BotCommand
        cmds = [
            BotCommand("play", "Play a song (ephemeral)", is_ephemeral=True),
            BotCommand("help", "Show help", is_ephemeral=False)
        ]
        await bot.set_bot_commands(cmds)
        await m.reply_text("✅ Ephemeral commands set!")
    except Exception as e:
        await m.reply_text(f"Failed to set ephemeral commands (API limitation): {e}")
