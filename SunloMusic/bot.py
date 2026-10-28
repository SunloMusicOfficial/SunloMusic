from pyrogram import Client
from SunloMusic.config import config
from SunloMusic.logger import LOGGER, get_startup_card

bot = None
assistant = None
ASSISTANT_CHATS = set() # ✅ Yaad rakhega kahan-kahan assistant already hai

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

# ✅ Naya Function: Assistant ko automatic join karwane ke liye
async def ensure_assistant_in_chat(chat_id: int) -> bool:
    global ASSISTANT_CHATS
    if not assistant:
        return False
        
    # Agar pehle se pata hai ki assistant group me hai
    if chat_id in ASSISTANT_CHATS:
        return True

    try:
        # Check karo ki assistant already member hai ya nahi
        await assistant.get_chat_member(chat_id, "me")
        ASSISTANT_CHATS.add(chat_id)
        return True
    except Exception:
        # Agar member nahi hai, toh join karne ki koshish karo
        LOGGER.info(f"🤖 Assistant is not in {chat_id}, trying to join...")
        try:
            # Public group ya direct ID se join
            await assistant.join_chat(chat_id)
            ASSISTANT_CHATS.add(chat_id)
            LOGGER.info(f"✅ Assistant joined {chat_id} successfully!")
            return True
        except Exception as e:
            LOGGER.warning(f"⚠️ Direct join failed: {e}. Trying invite link...")
            try:
                # Private group ke liye Bot se invite link banwao
                link = await bot.export_chat_invite_link(chat_id)
                await assistant.join_chat(link)
                ASSISTANT_CHATS.add(chat_id)
                LOGGER.info(f"✅ Assistant joined via invite link in {chat_id}!")
                return True
            except Exception as e2:
                LOGGER.error(f"❌ Assistant completely failed to join {chat_id}: {e2}")
                return False
