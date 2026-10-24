import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

@Client.on_message(filters.command("genstring") & filters.private)
async def genstring_cmd(client: Client, message: Message):
    await message.reply_text("🔑 **String Session Generator**\n\nYe command abhi external secure script (e.g. repl.it) ke through chalani chahiye taaki aapka number safe rahe. \n\n*Server par host karne se pehle Assistant account login karne ke liye main aapko ek secure Pyrogram v2 string generator link provide karunga!*")
