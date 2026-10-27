import asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.database import set_auth, get_all_chats, get_stats
from SunloMusic.decorators import sudo_only, admin_only

@bot.on_message(filters.command("auth") & filters.group)
@admin_only
async def auth_cmd(_, m):
    await set_auth(m.chat.id, True)
    await m.reply_text("✅ Authorized")

@bot.on_message(filters.command("stats"))
@sudo_only
async def stats_cmd(_, m):
    s = await get_stats()
    await m.reply_text(f"👥 Users: {s['users']}\n💬 Chats: {s['chats']}")

@bot.on_message(filters.command("broadcast"))
@sudo_only
async def bc_cmd(_, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a message.")
    chats = await get_all_chats()
    await m.reply_text(f"Broadcasting to {len(chats)} chats...")
    for c in chats:
        try: await m.reply_to_message.copy(c)
        except: pass
        await asyncio.sleep(0.1)
    await m.reply_text("✅ Done")
