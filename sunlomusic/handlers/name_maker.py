# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# 15 Premium Fonts
FONTS = {
    "smallcaps": "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
    "gothic": "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅",
    "gothic_lower": "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟",
    "double": "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ",
    "double_lower": "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫",
    "bold": "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭",
    "bold_lower": "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇",
    "cursive": "𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵",
    "cursive_lower": "𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏",
    "bold_cursive": "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩",
    "bold_cursive_lower": "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃",
    "monospace": "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉",
    "monospace_lower": "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣",
    "circle": "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ",
    "circle_lower": "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ",
    "square": "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉",
    "fullwidth": "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
    "fullwidth_lower": "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
}

# Premium Borders (Exact vibes from your screenshots)
BORDERS = [
    "⊹⊱♡ {name} ♡⊰⊹", "乂✿꧁ {name} ꧂✿乂", "▄︻デ {name} ══━一", "☬༒⋆ {name} ⋆༒☬", 
    "▰▰▰ {name} ▰▰▰", "➳❥ {name} ❥➳", "꧁☆☬ {name} ☬☆꧂", "【★】 {name} 【★】", 
    "✧･ﾟ: * {name} *:･ﾟ✧", "『 {name} 』", "▚▞ {name} ▞▚", "❖ {name} ❖", 
    "♔ {name} ♔", "╰┈➤ {name}", "✰ {name} ✰", "✿ {name} ✿", "⚜ {name} ⚜",
    "•´¯`•. {name} .•´¯`•", "░▒▓█ {name} █▓▒░", "×º°”˜`”°º× {name} ×º°”˜`”°º×",
    "꧁⫷ {name} ⫸꧂", "┊ {name} ┊", "⊰ {name} ⊱", "☯ {name} ☯", "♨ {name} ♨",
    "▰ {name} ▰", "✵ {name} ✵", "⟡ {name} ⟡", "❃ {name} ❃", "♛ {name} ♛",
    "🎀 {name} 🎀", "🌙 {name} 🌙", "🌟 {name} 🌟", "❥〆 {name} 〆❥", "↫↫ {name} ↬↬"
]

def generate_designs(name):
    designs = set()
    
    # 1. Pure Fonts
    for font in ["smallcaps", "gothic", "double", "bold", "cursive", "bold_cursive", "monospace", "circle", "square", "fullwidth"]:
        # Mix case for pure fonts
        parts = name.split()
        formatted_words = []
        for word in parts:
            if font == "smallcaps":
                formatted_words.append(word.lower().translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font])))
            elif font == "gothic":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "double":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "bold":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "cursive":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "bold_cursive":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "monospace":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "circle":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
            elif font == "square":
                formatted_words.append(word.upper().translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])))
            elif font == "fullwidth":
                formatted_words.append(word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS[font])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS[font+"_lower"])))
        designs.add(" ".join(formatted_words))

    # 2. Borders + Fonts Combinations
    for border in BORDERS:
        # Bold
        b_name = name.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS["bold"])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS["bold_lower"]))
        designs.add(border.format(name=b_name))
        
        # Small Caps
        sc_name = name.lower().translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS["smallcaps"]))
        designs.add(border.format(name=sc_name))
        
        # Bold Cursive
        bc_name = name.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS["bold_cursive"])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS["bold_cursive_lower"]))
        designs.add(border.format(name=bc_name))

        # Mixed Gothic
        g_name = name.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", FONTS["gothic"])).translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", FONTS["gothic_lower"]))
        designs.add(border.format(name=g_name))
        
    return list(designs)

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

        status = await message.reply_text("✨ **Generating 150+ Premium Designs... Please Wait**")
        
        results = generate_designs(text)
        
        # Send in chunks to prevent Telegram limit crash
        chunk = ""
        for res in results:
            if len(chunk) + len(res) > 3500:
                await message.reply_text(chunk, disable_web_page_preview=True)
                chunk = ""
                await asyncio.sleep(1) # 1 sec delay to prevent flood
            chunk += res + "\n\n"
            
        if chunk:
            await message.reply_text(chunk, disable_web_page_preview=True)
            
        await status.delete()
