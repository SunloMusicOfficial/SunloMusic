import asyncio
from pyrogram import Client, enums
from pyrogram.errors import UserAlreadyParticipant, UserBannedInChannel, FloodWait
from SunloMusic.config import config
from SunloMusic.logger import LOGGER, get_startup_card

bot = None
assistant = None

def init_clients():
    global bot, assistant
    bot = Client("SunloMusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, in_memory=True)
    if config.SESSION_STRING:
        assistant = Client("SunloAssistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_STRING, in_memory=True)

async def start_bot():
    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username}")
    if assistant:
        await assistant.start()
        LOGGER.info("✅ Assistant started (VC Ready)")
    if config.LOGGER_ID:
        try: await bot.send_message(config.LOGGER_ID, get_startup_card(me.username))
        except: pass

async def ensure_assistant_in_chat(chat_id: int) -> str:
    if not assistant: return "failed"

    try:
        member = await bot.get_chat_member(chat_id, assistant.me.id)
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]: return "banned"
        if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return "ok"
    except: pass

    try:
        member = await assistant.get_chat_member(chat_id, "me")
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]: return "banned"
        if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return "ok"
    except Exception as e:
        if "USER_BANNED" in str(e).upper(): return "banned"

    try:
        chat = await bot.get_chat(chat_id)
        if chat.username:
            try:
                await assistant.join_chat(chat.username)
                return "ok"
            except UserAlreadyParticipant: return "ok"
            except Exception as e:
                if "USER_BANNED" in str(e).upper(): return "banned"
    except: pass

    try:
        try: link = await bot.export_chat_invite_link(chat_id)
        except Exception as e:
            if "CHAT_ADMIN_REQUIRED" in str(e).upper(): return "failed_no_admin"
            raise e
            
        await asyncio.sleep(1)
        try: await assistant.join_chat(link)
        except UserAlreadyParticipant: return "ok"
        except Exception as e:
            if "USER_BANNED" in str(e).upper(): return "banned"
            
        await asyncio.sleep(2) 
        try:
            member = await assistant.get_chat_member(chat_id, "me")
            if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]: return "banned"
            return "ok"
        except:
            try:
                me_ass = await assistant.get_me()
                await bot.approve_chat_join_request(chat_id, me_ass.id)
                return "ok"
            except: pass
        return "ok" 
    except Exception as e:
        if "USER_BANNED" in str(e).upper(): return "banned"

    return "failed"

async def send_ban_alert(chat_id: int):
    """Sends premium ban alert card to chat tagging all admins"""
    from richgram import rich_send, rich_button, rich_button_row
    
    if not assistant: return
    
    try:
        ass_me = await assistant.get_me()
        ass_username = ass_me.username
        ass_id = ass_me.id
    except:
        ass_username = "Assistant"
        ass_id = 0
    
    admins = []
    try:
        async for admin in bot.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not admin.user.is_bot and not admin.user.is_deleted:
                admins.append(admin.user.mention)
    except: pass
    
    admins_text = " ".join(admins[:10]) if admins else "Admins"
    if len(admins) > 10:
        admins_text += " and others..."
    
    card_text = (
        f'<blockquote>'
        f'🚫 <b>ASSISTANT BANNED</b> 🚫\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'⚠️ The Voice Chat Assistant has been restricted in this group.\n'
        f'</blockquote>\n\n'
        f'🤖 <b>Assistant Info:</b>\n'
        f'• Username: <code>@{ass_username}</code>\n'
        f'• ID: <code>{ass_id}</code>\n\n'
        f'🛠️ <b>How to fix:</b>\n'
        f'1. Manually unban <b>@{ass_username}</b> from group settings\n'
        f'2. Or click the button below to auto-unban\n\n'
        f'<blockquote>{admins_text}\n\n<b>Please take action!</b></blockquote>'
    )
    
    # ✅ FIXED: Use rich_button instead of InlineKeyboardMarkup
    buttons = (
        rich_button_row(rich_button("🔓 Unban Assistant Now", callback_data="unban_assistant", style="success")) +
        rich_button_row(rich_button("❌ Dismiss", callback_data="dismiss_ban", style="danger"))
    )
    
    try:
        await rich_send(bot, chat_id, card_text + buttons)
    except Exception as e:
        LOGGER.error(f"Ban alert error: {e}")
