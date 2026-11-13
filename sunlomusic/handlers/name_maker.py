# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# --- Premium Unicode Fonts ---
FONTS = {
    "bold": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "bold_map": "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    
    "italic": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "italic_map": "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻",
    
    "gothic": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "gothic_map": "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷",
    
    "double": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "double_map": "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    
    "script": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "script_map": "𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏",
    
    "circle": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "circle_map": "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ⓪①②③④⑤⑥⑦⑧⑨",
    
    "square": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "square_map": "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉",
    
    "smallcaps": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "smallcaps_map": "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
    
    "fullwidth": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "fullwidth_map": "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９",
}

# --- Premium Borders ---
BORDERS = [
    "⊹⊱♡ {name} ♡⊰⊹", "乂✿꧁ {name} ꧂✿乂", "▄︻デ {name} ══━一", "☬༒⋆ {name} ⋆༒☬", 
    "▰▰▰ {name} ▰▰▰", "➳❥ {name} ❥➳", "꧁☆☬ {name} ☬☆꧂", "【★】 {name} 【★】", 
    "✧･ﾟ: * {name} *:･ﾟ✧", "『 {name} 』", "▚▞ {name} ▞▚", "❖ {name} ❖", 
    "♔ {name} ♔", "╰┈➤ {name}", "✰ {name} ✰", "✿ {name} ✿", "⚜ {name} ⚜"
]

def apply_font(text, font_key, map_key):
    source = FONTS[font_key]
    target = FONTS[map_key]
    trans = str.maketrans(source, target)
    return text.translate(trans)

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
            
        if len(text) > 15:
            await message.reply_text("**Name is too long! Please provide a shorter name (max 15 chars).**")
            return

        status = await message.reply_text("✨ **Generating Premium Styles...**")
        
        results = []
        
        # 1. Generate Pure Fonts (Bina border ke, jaise screenshot mein hai)
        for font in ["bold", "gothic", "double", "script", "circle", "smallcaps", "fullwidth"]:
            styled_text = apply_font(text, font, f"{font}_map")
            results.append(styled_text)
            
        # 2. Generate Font + Border Combos
        for border in BORDERS:
            for font in ["bold", "gothic", "double", "script"]:
                styled_text = apply_font(text, font, f"{font}_map")
                formatted = border.format(name=styled_text)
                results.append(formatted)

        # Send in chunks
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
