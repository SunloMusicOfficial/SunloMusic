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

    # 1. Check status via Bot (Most accurate)
    try:
        member = await bot.get_chat_member(chat_id, assistant.me.id)
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
            return "banned"
        if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return "ok"
    except Exception: pass

    # 2. Fallback to Assistant check
    try:
        member = await assistant.get_chat_member(chat_id, "me")
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
            return "banned"
        if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return "ok"
    except Exception as e:
        if "USER_BANNED" in str(e).upper(): return "banned"

    # 3. Try joining
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
