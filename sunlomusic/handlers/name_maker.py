# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

STYLES = [
    "♡⊹⊱ {name} ⊰⊹♡", "✧･ﾟ: *{name}*:･ﾟ✧", "꧁༺ {name} ༻꧂", "✿ {name} ✿", "♛ {name} ♛", "⚡ {name} ⚡", "🔥 {name} 🔥", 
    "🎀 {name} 🎀", "💎 {name} 💎", "🌙 {name} 🌙", "🌟 {name} 🌟", "🎵 {name} 🎵", "👑 {name} 👑", "☬ {name} ☬", 
    "❥ {name} ❥", "☠ {name} ☠", "✰ {name} ✰", "⨳ {name} ⨳", "┊ {name} ┊", "⊰ {name} ⊱", "❖ {name} ❖", "⚜ {name} ⚜", 
    "☯ {name} ☯", "♨ {name} ♨", "❀ {name} ❀", "『 {name} 』", "▰ {name} ▰", "✧ {name} ✧", "♡ {name} ♡", "✦ {name} ✦", 
    "✦•┈๑⋅⋯ {name} ⋯⋅๑┈•✦", "▚▞ {name} ▚▞", "▞▚ {name} ▞▚", "╰┈➤ {name}", "➳ {name}", "❥〆 {name} 〆❥", "↫↫ {name} ↬↬", 
    "⊹⊱ {name} ⊰⊹", "•´¯`•. {name} .•´¯`•", "°•. {name} .•°", "✼ {name} ✼", "✾ {name} ✾", "❁ {name} ❁", "☸ {name} ☸", 
    "♔ {name} ♔", "♕ {name} ♕", "♖ {name} ♖", "♗ {name} ♗", "꧁☆ {name} ☆꧂", "꧁💞 {name} 💞꧂", "꧁ঔৣ☬✞ {name} ✞☬ঔৣ꧂", 
    "•♡• {name} •♡•", "☆━ {name} ━☆", "♥ {name} ♥", "✩ {name} ✩", "✪ {name} ✪", "✫ {name} ✫", "✬ {name} ✬", 
    "✭ {name} ✭", "✮ {name} ✮", "✯ {name} ✯", "┏━ {name} ━┓", "┗━ {name} ━┛", "╔═ {name} ═╗", "╚═ {name} ═╝", 
    "▄︻デ {name} ══━一", "◥꧁ད {name} ཌ꧂◤", "꧁༒☬ {name} ☬༒꧂", "꧁⫷ {name} ⫸꧂", "⫷ {name} ⫸", "❮ {name} ❯", "【 {name} 】", 
    "〖 {name} 〗", "〔 {name} 〕", "《 {name} 》", "「 {name} 」", "☆ {name} ☆", "★ {name} ★", "○ {name} ○", 
    "● {name} ●", "◎ {name} ◎", "◇ {name} ◇", "◆ {name} ◆", "□ {name} □", "■ {name} ■", "△ {name} △", 
    "▲ {name} ▲", "▽ {name} ▽", "▼ {name} ▼", "✿•°¯`•• {name} ••´¯°•✿", "⫸⫷ {name} ⫸⫷", "➶ {name} ➴",
    "⇝ {name} ⇜", "☾ {name} ☽", "✵ {name} ✵", "⊱ {name} ⊰", "⋆ {name} ⋆", "⟡ {name} ⟡", "❃ {name} ❃"
]

def register_name_maker(app: Client):
    @app.on_message(filters.command("name"))
    async def name_command(client, message: Message):
        text = ""
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        elif len(message.text.split()) > 1:
            text = message.text.split(maxsplit=1)[1]
            
        if not text:
            await message.reply_text("**Usage:**\n`/name Sakil` \nYa kisi ke message par reply karke `/name` likhein.")
            return
            
        if len(text) > 20:
            await message.reply_text("**Name is too long! Please provide a shorter name (max 20 chars).**")
            return

        status = await message.reply_text("✨ **Generating Stylish Names, please wait...**")
        
        results = [style.format(name=text) for style in STYLES]
        
        # Send in chunks to avoid message length limits
        chunk = ""
        for res in results:
            if len(chunk) + len(res) > 3500:
                await message.reply_text(chunk, disable_web_page_preview=True)
                chunk = ""
                await asyncio.sleep(0.5) # prevent flood
            chunk += res + "\n\n"
            
        if chunk:
            await message.reply_text(chunk, disable_web_page_preview=True)
            
        await status.delete()
