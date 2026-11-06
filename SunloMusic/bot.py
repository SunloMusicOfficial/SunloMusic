import asyncio
from pyrogram import Client, enums
from pyrogram.errors import InviteHashExpired, UserAlreadyParticipant, UserBannedInChannel
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
    if not assistant: return "failed"

    # 1. Check current status (No Cache - Strict Check)
    try:
        member = await assistant.get_chat_member(chat_id, "me")
        if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
            return "banned"
        return "ok"
    except Exception:
        pass # Not in chat, proceed to join

    LOGGER.info(f"🤖 Assistant is not in {chat_id}, attempting to join...")
    
    # 2. Try Public Username
    try:
        chat = await bot.get_chat(chat_id)
        if chat.username:
            try:
                await assistant.join_chat(chat.username)
                return "ok"
            except UserAlreadyParticipant:
                return "ok"
            except UserBannedInChannel:
                return "banned"
            except Exception as e:
                if "USER_BANNED_IN_CHAT" in str(e).upper() or "USER_BANNED_IN_CHANNEL" in str(e).upper():
                    return "banned"
    except: pass

    # 3. Try Invite Link
    try:
        link = await bot.export_chat_invite_link(chat_id)
        await asyncio.sleep(1)
        try:
            await assistant.join_chat(link)
        except Exception as e:
            if "USER_BANNED_IN_CHAT" in str(e).upper() or "USER_BANNED_IN_CHANNEL" in str(e).upper():
                return "banned"
            
        await asyncio.sleep(2) # Wait for Telegram to process
        
        try:
            member = await assistant.get_chat_member(chat_id, "me")
            if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
                return "banned"
            return "ok"
        except:
            # Auto-approve join request
            try:
                me_ass = await assistant.get_me()
                await bot.approve_chat_join_request(chat_id, me_ass.id)
                return "ok"
            except: pass
    except Exception as e:
        LOGGER.error(f"❌ Could not join: {e}")
        if "USER_BANNED_IN_CHAT" in str(e).upper() or "USER_BANNED_IN_CHANNEL" in str(e).upper():
            return "banned"

    return "failed"
