# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# Exact Font Maps seen in your screenshots
FONT_MAPS = {
    "smallcaps": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"),
    "gothic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"),
    "double": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
    "square": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉"),
    "bold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "cursive": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏")
}

# Exact Border Combinations from your screenshots
DESIGNS = [
    "❤ ╰⊹{name}⊹╯ ❤",
    "꧁༺ {name_gothic} ༻꧂",
    "╰┈➤ {name}",
    "▄︻デ {name} ══━一",
    "乂✿꧁ {name} ꧂✿乂",
    "♡⊹⊱ {name} ⊰⊹♡",
    "✧･ﾟ: * {name} *:･ﾟ✧",
    "༆ {name_square} ༆",
    "ღ꧁ღ⊱ {name} ⊱ღ꧂ღ",
    "▰▰▰ {name} ▰▰▰",
    "⎝⎝✧ {name} ✧⎠⎠",
    "➳❥ {name} ❥➳",
    "☬༒⋆ {name} ⋆༒☬",
    "【★】 {name} 【★】",
    "✰ {name} ✰",
    "★彡 {name} 彡★",
    "꧁⫷ {name} ⫸꧂",
    "⫷ {name} ⫸",
    "✧･ﾟ: *{name_bold}*:･ﾟ✧",
    "『 {name_cursive} 』"
]

def register_name_maker(app: Client):
    @app.on_message(filters.command("name"))
    async def name_command(client, message: Message):
        text = ""
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text.strip()
        elif len(message.text.split()) > 1:
            text = message.text.split(maxsplit=1)[1].strip()
            
        if not text:
            await message.reply_text("**Usage:**\n`/name Sakil` \nYa kisi ke message par reply karke `/name` likhein.")
            return
            
        if len(text) > 15:
            await message.reply_text("**Name is too long! Please provide a shorter name (max 15 chars).**")
            return

        status = await message.reply_text("✨ **Generating Premium Designs...**")
        
        results = []
        
        # Generate exact combinations
        for design in DESIGNS:
            # Prepare all font variations
            formatted = design.format(
                name=text,
                name_smallcaps=text.translate(FONT_MAPS["smallcaps"]),
                name_gothic=text.translate(FONT_MAPS["gothic"]),
                name_double=text.translate(FONT_MAPS["double"]),
                name_square=text.translate(FONT_MAPS["square"]).upper(),
                name_bold=text.translate(FONT_MAPS["bold"]),
                name_cursive=text.translate(FONT_MAPS["cursive"])
            )
            results.append(formatted)

        # Send in chunks to avoid message limit
        chunk = ""
        for res in results:
            if len(chunk) + len(res) > 3500:
                await message.reply_text(chunk, disable_web_page_preview=True)
                chunk = ""
                await asyncio.sleep(0.5) 
            chunk += res + "\n\n"
            
        if chunk:
            await message.reply_text(chunk, disable_web_page_preview=True)
            
        await status.delete()
