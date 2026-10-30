from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot, assistant
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors

async def send_bot_log(text):
    if config.LOGGER_ID:
        try: await bot.send_message(config.LOGGER_ID, text)
        except: pass
    if config.OWNER_ID:
        try: await bot.send_message(config.OWNER_ID, text)
        except: pass

@bot.on_message(filters.new_chat_members)
@catch_errors
async def log_added(_, m: Message):
    me = await bot.get_me()
    for user in m.new_chat_members:
        if user.id == me.id or (assistant and user.id == assistant.me.id):
            client = "Bot" if user.id == me.id else "Assistant"
            try:
                link = f"https://t.me/{m.chat.username}" if m.chat.username else (await m.chat.export_chat_invite_link() if not m.chat.username else "Private Group")
            except: link = "Private/Link Unavailable"
            
            text = (
                f"<b>➕ {client} Added to Group!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Added By:</b> {m.from_user.mention}\n"
                f"🆔 <b>User ID:</b> <code>{m.from_user.id}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💬 <b>Group:</b> {m.chat.title}\n"
                f"🆔 <b>Group ID:</b> <code>{m.chat.id}</code>\n"
                f"🔗 <b>Link:</b> <a href='{link}'>Click Here</a>\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            await send_bot_log(text)

@bot.on_message(filters.left_chat_member)
@catch_errors
async def log_removed(_, m: Message):
    me = await bot.get_me()
    if m.left_chat_member.id == me.id or (assistant and m.left_chat_member.id == assistant.me.id):
        client = "Bot" if m.left_chat_member.id == me.id else "Assistant"
        text = (
            f"<b>➖ {client} Removed from Group!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Removed By:</b> {m.from_user.mention}\n"
            f"🆔 <b>User ID:</b> <code>{m.from_user.id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 <b>Group:</b> {m.chat.title}\n"
            f"🆔 <b>Group ID:</b> <code>{m.chat.id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await send_bot_log(text)
