from pyrogram import Client
from pyrogram.raw import functions
from utils.logger import LOGGER

async def auto_start_vc(client: Client, chat_id: int) -> bool:
    try:
        # Pyrogram raw API to start Group Call (Voice Chat)
        peer = await client.resolve_peer(chat_id)
        await client.invoke(
            functions.phone.CreateGroupCall(
                peer=peer,
                random_id=client.rnd_id() // 9000000000,
                rtmp_stream=False
            )
        )
        return True
    except Exception as e:
        LOGGER.error(f"Failed to auto-start VC: {e}")
        return False
