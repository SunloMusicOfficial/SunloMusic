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
            except Exception as e:
                LOGGER.warning(f"⚠️ Public join failed: {e}")
    except: pass

    # 3. Try Primary Invite Link (export_chat_invite_link - Most Reliable)
    try:
        link = await bot.export_chat_invite_link(chat_id)
        await asyncio.sleep(2) # Delay for Telegram to process the link
        try:
            await assistant.join_chat(link)
            ASSISTANT_CHATS.add(chat_id)
            LOGGER.info(f"✅ Assistant joined via primary invite link")
            return True
        except InviteHashExpired:
            LOGGER.warning("⚠️ Primary link expired, trying fresh link...")
    except: pass

    # 4. Try Fresh Invite Link (No member limit, No expiry)
    try:
        invite = await bot.create_chat_invite_link(chat_id, name="Auto Join", member_limit=0)
        await asyncio.sleep(2) # Crucial delay
        try:
            await assistant.join_chat(invite.invite_link)
            ASSISTANT_CHATS.add(chat_id)
            LOGGER.info(f"✅ Assistant joined via fresh invite link")
            return True
        except InviteHashExpired:
            LOGGER.error("❌ Fresh link also expired. Telegram might be blocking the join.")
            try: await bot.revoke_chat_invite_link(chat_id, invite.invite_link)
            except: pass
    except Exception as e:
        LOGGER.error(f"❌ Could not create invite link: {e} (Check Bot Admin Rights)")

    return False
