import asyncio
from pyrogram import Client
from pyrogram.errors import InviteHashExpired, UserAlreadyParticipant
from SunloMusic.config import config
from SunloMusic.logger import LOGGER, get_startup_card

bot = None
assistant = None
ASSISTANT_CHATS = set()

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

async def ensure_assistant_in_chat(chat_id: int) -> bool:
    global ASSISTANT_CHATS
    if not assistant: return False
        
    if chat_id in ASSISTANT_CHATS: return True

    # 1. Check if already a member
    try:
        await assistant.get_chat_member(chat_id, "me")
        ASSISTANT_CHATS.add(chat_id)
        return True
    except Exception:
        pass

    LOGGER.info(f"🤖 Assistant is not in {chat_id}, attempting to join...")
    
    # 2. Try Public Username
    try:
        chat = await bot.get_chat(chat_id)
        if chat.username:
            try:
                await assistant.join_chat(chat.username)
                ASSISTANT_CHATS.add(chat_id)
                LOGGER.info(f"✅ Assistant joined public chat @{chat.username}")
                return True
            except UserAlreadyParticipant:
                ASSISTANT_CHATS.add(chat_id)
                return True
            except Exception:
                pass
    except: pass

    # 3. Try Invite Link + Auto-Approve (Fixes the manual approval issue)
    try:
        link = await bot.export_chat_invite_link(chat_id)
        await asyncio.sleep(1)
        try:
            await assistant.join_chat(link)
        except Exception as e:
            # Sometimes join_chat throws error if request is pending
            LOGGER.info(f"Join attempt: {e}")
            
        await asyncio.sleep(2) # Wait for Telegram to process
        
        # Check if joined
        try:
            await assistant.get_chat_member(chat_id, "me")
            ASSISTANT_CHATS.add(chat_id)
            LOGGER.info(f"✅ Assistant joined via invite link")
            return True
        except:
            # ✅ If still not joined, Bot auto-approves the join request!
            LOGGER.info("📝 Assistant join request pending. Bot auto-approving...")
            try:
                me_ass = await assistant.get_me()
                await bot.approve_chat_join_request(chat_id, me_ass.id)
                LOGGER.info("✅ Bot auto-approved Assistant's request!")
                ASSISTANT_CHATS.add(chat_id)
                return True
            except Exception as approve_err:
                LOGGER.error(f"❌ Auto-approve failed: {approve_err}. Make sure Bot has 'Add Users' permission.")
    except Exception as e:
        LOGGER.error(f"❌ Could not create invite link: {e}")

    return False
