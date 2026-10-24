import random
from pyrogram import Client, filters
from pyrogram.types import Message

AFK_USERS = {}

@Client.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client: Client, message: Message):
    # Tags everyone in the group (Simple version for limit safety)
    await message.reply_text("🔔 **Calling all members!**\nPay attention to the chat!")

@Client.on_message(filters.command("afk"))
async def afk_cmd(client: Client, message: Message):
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "Busy"
    AFK_USERS[message.from_user.id] = reason
    await message.reply_text(f"💤 {message.from_user.mention} is now AFK.\nReason: {reason}")

@Client.on_message(filters.command(["dice", "dart", "toss"]))
async def fun_games(client: Client, message: Message):
    cmd = message.command[0]
    emoji = "🎲" if cmd == "dice" else "🎯" if cmd == "dart" else random.choice(["🪙 Heads", "🪙 Tails"])
    
    if cmd == "toss":
        await message.reply_text(f"Result: **{emoji}**")
    else:
        await client.send_dice(message.chat.id, emoji=emoji)
