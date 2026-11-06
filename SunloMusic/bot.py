import asyncio
from pyrogram import Client, enums
from pyrogram.errors import InviteHashExpired, UserAlreadyParticipant, UserBannedInChannel, FloodWait
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
    else:
        LOGGER.warning("⚠️ No SESSION_STRING provided.")
        
    if config.LOGGER_ID:
        try:
            await bot.send_message(config.LOGGER_ID, get_startup_card(me.username))
        except Exception as e:
            LOGGER.error(f"Failed to send startup card: {e}")

async def ensure_assistant_in_chat(chat_id: int) -> str:
    """Returns 'ok', 'banned', or 'failed'"""
    if not assistant: 
        LOGGER.error("❌ Assistant client not initialized!")
        return "failed"

    # 1. Check current status
    try:
        member = await assistant.get_chat_member(chat_id, "me")
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
            LOGGER.warning(f"🚫 Assistant is BANNED in chat {chat_id}")
            return "banned"
        LOGGER.info(f"✅ Assistant is already in chat {chat_id}")
        return "ok"
    except FloodWait as e:
        LOGGER.warning(f"⚠️ FloodWait on get_chat_member: {e.value}s")
        await asyncio.sleep(e.value)
    except Exception as e:
        err = str(e).upper()
        if "USER_BANNED_IN_CHAT" in err or "USER_BANNED_IN_CHANNEL" in err:
            LOGGER.warning(f"🚫 Assistant is BANNED in chat {chat_id}")
            return "banned"
        # User is not in chat, proceed to join
        LOGGER.info(f"🤖 Assistant is not in chat {chat_id}, attempting to join...")
        pass

    # 2. Try Public Username
    try:
        chat = await bot.get_chat(chat_id)
        if chat.username:
            LOGGER.info(f"🔗 Trying to join public chat @{chat.username}")
            try:
                await assistant.join_chat(chat.username)
                LOGGER.info(f"✅ Joined public chat @{chat.username}")
                return "ok"
            except UserAlreadyParticipant:
                return "ok"
            except UserBannedInChannel:
                LOGGER.warning(f"🚫 Assistant is BANNED in @{chat.username}")
                return "banned"
            except Exception as e:
                LOGGER.error(f"❌ Failed to join public chat: {e}")
                err = str(e).upper()
                if "USER_BANNED" in err: return "banned"
    except Exception as e:
        LOGGER.info(f"Could not fetch public chat info: {e}")

    # 3. Try Invite Link
    try:
        LOGGER.info(f"🔗 Exporting invite link for chat {chat_id}")
        link = await bot.export_chat_invite_link(chat_id)
        await asyncio.sleep(1)
        try:
            await assistant.join_chat(link)
            LOGGER.info(f"✅ Joined private chat via link")
        except UserAlreadyParticipant:
            return "ok"
        except Exception as e:
            LOGGER.error(f"❌ Failed to join via link: {e}")
            err = str(e).upper()
            if "USER_BANNED" in err: return "banned"
            if "ALREADY_PARTICIPANT" in err: return "ok"
            
        await asyncio.sleep(2) # Wait for Telegram to process
        
        try:
            member = await assistant.get_chat_member(chat_id, "me")
            if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
                return "banned"
            return "ok"
        except:
            LOGGER.info(f"⏳ Assistant join request pending. Bot attempting to auto-approve...")
            try:
                me_ass = await assistant.get_me()
                await bot.approve_chat_join_request(chat_id, me_ass.id)
                LOGGER.info(f"✅ Auto-approved assistant join request!")
                return "ok"
            except Exception as approve_err:
                LOGGER.error(f"❌ Auto-approve failed: {approve_err}")
                
        return "ok" 
        
    except Exception as e:
        LOGGER.error(f"❌ Bot could not export invite link. Is bot an admin? Error: {e}")
        err = str(e).upper()
        if "USER_BANNED" in err: return "banned"

    LOGGER.error(f"❌ All join methods failed for chat {chat_id}")
    return "failed"
