# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# 1. Premium Fonts Dictionary
FONTS = {
    "bold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "cursive": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
    "gothic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"),
    "double": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
    "smallcaps": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"),
    "circle": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
    "square": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉"),
    "fullwidth": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")
}

# 2. User's Exact 66 Borders
USER_BORDERS = [
    "❤️‍🔥 ⃪꯭⃝꯭꯭꯭꯭꯭꯭꯭{n}👻𝆺꯭𝅥⎯꯭̽⎯꯭",
    "🦋⃤✺꯭⤹⌯꯭🫥꯭꯭꯭꯭꯭꯭꯭꯭𝆬{n}🌙꯭🐬᪵᪳𝄟",
    "꧁𓊈𒆜꯭꯭꯭꯭꯭꯭꯭{n}𒆜𓊉꧂",
    "🍹𝆺𝅥⃝🤍⃪⃪꯭꯭㉿ ꯭꯭꯭꯭꯭꯭꯭꯭͓{n}◡̈⃝🤍͕᪳𝆺꯭𝅥⎯꯭̽⎯꯭",
    "➳↡↡↡↡↡☬꯭꯭꯭꯭꯭꯭꯭{n}☬↡↡↡↡↡➳",
    "✧⊹⊱⍣⊹⊱꯭꯭꯭꯭꯭꯭꯭{n}⊹⊱⍣⊹⊰✧",
    "◄⏤͟͟͞ ⃪ͥ͢𐏓⃝⃪⭕ғͥғ𓆩꯭꯭꯭꯭꯭꯭꯭{n}𓆪••➤‌‌",
    "𝄟͢ᶦ―ᷟ⃞꯭꯭꯭꯭꯭꯭꯭᪵{n}𝄟⃝🤫᭄",
    "̶̶ ̶꯭͓̽♥️ ⃪꯭꯭꯭꯭꯭꯭꯭꯭⃜{n}᭡፝֟፝֟͢🍃اا̽ـ꯭ــ꯭ـ⃛و꯭",
    "˟ ̶꯭⃖ ̶꯭꯭🪂⃪꯭⃝꯭꯭꯭꯭꯭꯭꯭{n}𓆩🥵꯭𓆪",
    ".⎯꯭᪵᪳🦋⃝‌꯭𝅦𝅥𝅥ٖٖ͟͟͟͟𝄀𝄄𝄀꯭꯭꯭꯭꯭꯭꯭꯭͟͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "◦•●◉✿ ꯭꯭꯭꯭꯭꯭꯭{n} ✿◉●•◦",
    "╰•★★ ꯭꯭꯭꯭꯭꯭꯭{n} ★★•╯",
    "❁⭒☆꯭꯭꯭꯭꯭꯭꯭{n}☆⭒❁",
    "𓃭⃞꯭꯭꯭꯭꯭꯭꯭⃔͢{n}➼ ᭄꯭꯭❥𝄄⃟꯭𝅥ͦ𝆬🥂",
    "𓆩𓆪𓆩𓆪❖꯭꯭꯭꯭꯭꯭꯭{n}❖𓆩𓆪𓆩𓆪",
    "✪♕☬꯭꯭꯭꯭꯭꯭꯭{n}☬♕✪",
    "⎯꯭̽ᬃ꯭꯭꯭꯭꯭꯭꯭꯭{n}🧸⎯",
    "⏤⃝⃪꯭⃮͙͙⃕⃔🌺⃪꯭꯭꯭꯭꯭꯭꯭꯭͙͙𝆭{n}🤍⃪꯭͙͙⏤",
    "ミ★ ꯭꯭꯭꯭꯭꯭꯭{n} ★彡",
    "⫸⫷⫸⫷⫸✪꯭꯭꯭꯭꯭꯭꯭{n}✪⫸⫷⫸⫷⫸",
    "──⃜͢͢៎꯭꯭꯭🐼⃪꯭͓͢°⃪꯭𝆺꯭꯭꯭꯭꯭꯭꯭꯭𝅥{n} ꯭͢⃟͢🍒⛦⃕͜🍃",
    "꧁༒☬꯭꯭꯭꯭꯭꯭꯭{n}☬༒꧂",
    "𝁘꯭ ꯭ྭ꯭꯭꯭꯭꯭꯭꯭{n}➛🕸",
    "꧁✿✿✿ ꯭꯭꯭꯭꯭꯭꯭{n} ✿✿✿꧂",
    "༺༒❁꯭꯭꯭꯭꯭꯭꯭{n}❁༒༻",
    "𓄂≛⃝꯭꯭꯭꯭꯭꯭꯭꯭{n} ꯭𝅥ͦ𝆬🚭",
    "❘☞ͥ͟⋆ͣ͟⋆ͫ⍣꯭꯭꯭꯭꯭꯭꯭꯭{n}⍣❘꯭𝄄꯭",
    "꧁•⊹٭꯭꯭꯭꯭꯭꯭꯭{n}٭⊹•꧂",
    "个『꯭꯭꯭꯭꯭꯭꯭{n}』个",
    ".⎯᪵᪵፝֟፝֟⎯꯭𝄀𝄄𝄀🌸꯭꯭꯭꯭꯭꯭꯭꯭꯭͟{n}🦋",
    "⎯͢ꠋ ᶦϻͣ། ⃪ͥ͢ 🌺꯭꯭꯭꯭꯭꯭꯭͜͟{n}🫧",
    "𒆜꯭•☬•꯭꯭꯭꯭꯭꯭꯭{n}•☬•꯭𒆜",
    "✤𖠌𓂀✤ ꯭꯭꯭꯭꯭꯭꯭{n} ✤𓂀𖠌✤",
    "˚₊·𐏓꯭ᶜᵘᵗᵉ ꯭꯭꯭꯭꯭꯭꯭{n}°‌🥀",
    "ıllıllı⭐🌟 ꯭꯭꯭꯭꯭꯭꯭{n} 🌟⭐ıllıllı",
    "◄🕊️⃪꯭꯭꯭꯭꯭꯭꯭꯭̽͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "ᯓ🩺̶̶᪵˟̶ 𝆺𝅥⃝🫀꯭꯭꯭꯭꯭꯭꯭꯭{n}ﮩ᪵٨ـﮩ➛♥️",
    "⋆⋆⋆❀꯭꯭꯭꯭꯭꯭꯭{n}❀⋆⋆⋆",
    "•─┼ᶦϻ‌།͢ ⃪꯭꯭꯭꯭꯭꯭꯭{n}🍓꯭᪳᪼᪳",
    "亗『꯭꯭꯭꯭꯭꯭꯭{n}』亗",
    "◄⏤͟͟͞🤍⃝⃪🦋⃪꯭ᵛ̲ᵎ̲ᵖ̲𒉜꯭꯭꯭꯭꯭꯭꯭{n}🌸︭︫┼⁰⁰⁷─⦁••",
    "°†° «[꯭꯭꯭꯭꯭꯭꯭{n}]» °†°",
    "☆☬꯭꯭꯭꯭꯭꯭꯭{n}☬☆",
    "⎯⃛㬓𓆩⃗㬓͟🍃̶̌͟🅼ɨֆֆ𝆺𝅥⃝꯭꯭꯭꯭꯭꯭꯭{n}˶֟፝͟͝⎯꯭̽ 🖤",
    "🥀 ⃪ͥ͢ ᷟ𝆺꯭꯭𝅥᪳‌꯭꯭꯭꯭꯭꯭꯭꯭{n} ⎯꯭꯭᪵᪵፝֟፝❤️‍🔥",
    "➶➶➶➶➶⫷꯭꯭꯭꯭꯭꯭꯭{n}⫸➶➶➶➶➶",
    "★¸.•☆•.¸★ ꯭꯭꯭꯭꯭꯭꯭{n} ★⡀.•☆•.★",
    "➤⇌⇌⇌꯭꯭꯭꯭꯭꯭꯭{n}⇌⇌⇌➤",
    "❖꯭𓂀⃝꯭꯭꯭꯭꯭꯭꯭{n}𓂀⃝꯭❖",
    "【★】➳✮꯭꯭꯭꯭꯭꯭꯭{n}✮➳【★】",
    "❥⃝⍣꯭꯭꯭꯭꯭꯭꯭{n}❥⃝⍣",
    "⛥꯭ᴳᴼᴰ⛥꯭꯭꯭꯭꯭꯭꯭꯭{n}⛥꯭",
    "🝐꯭𓆩꯭꯭⍣⃪꯭꯭꯭꯭꯭꯭꯭{n}⃪⍣꯭꯭𓆪꯭🝐",
    "◄❥ ⃝⃪⃕♥️̶⍣⃪͜🌿𝄄᭄꯭꯭꯭꯭꯭꯭꯭{n}🍃⃝🎸",
    "◄⏤͟͞ꭙ𝆺𝅥⃝🔥 ⃪꯭꯭꯭꯭꯭꯭꯭ͥ͢{n}༎ࠫ⛧‌ٖٖٖٖٖٖٜٖٖٖٖ𝆺꯭𝅥🤍",
    "☔️⃟⃚⃐⎯⃚꯭፝֟֗. ⃝꯭꯭꯭꯭꯭꯭꯭{n}✿⃟☔️✾",
    "★彡[꯭꯭꯭꯭꯭꯭꯭{n}]彡★",
    "𓄂꯭꯭‌≛⃝꯭꯭꯭‌꯭꯭꯭꯭꯭꯭꯭꯭{n}𐎭❥┼🕊️",
    "✿્᭄͜͡⃝❥꯭꯭꯭꯭꯭꯭꯭{n}༏༏𝆺꯭𝅥𝆺꯭𝅥༎ࠫ✿͜͡࿐",
    "•⏤‌𝄞⃝🍧 ‌⃪‌꯭꯭꯭꯭꯭꯭꯭{n}♥️꯭꯭꯭꯭ ꯭꯭᪳𝆺𝅥",
    "⎯ᷝ⎯ⷨ͢ ꯭꯭꯭꯭꯭꯭꯭{n}𝆺꯭𝅥❤️‍🔥⎯꯭ͯ⟶⋆",
    "──⃜͢͢🥤⃘⃝⃟⃪꯭꯭꯭꯭꯭꯭꯭⃜{n}༎͢🦋",
    "⤹ ⃪꯭꯭꯭꯭꯭꯭꯭꯭{n} ⃪🤭꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭",
    "⋆⎯꯭̽𝅃꯭꯭꯭꯭꯭꯭꯭꯭᳚{n}𝅃꯭꯭᳚ ⃪꯭⃝𐏓꯭",
    "𓂀 ꯭꯭꯭꯭꯭꯭꯭{n} 𓂀"
]

# 3. Extra Auto-Generated Borders
AUTO_BORDERS = [
    "『 {n} 』", "▰▰ {n} ▰▰", "✧･ﾟ: * {n} *:･ﾟ✧", "ღ꧁ღ⊱ {n} ⊱ღ꧂ღ", 
    "★彡 {n} 彡★", "▄︻デ {n} ══━一", "乂✿꧁ {n} ꧂✿乂", "☬༒⋆ {n} ⋆༒☬",
    "✰ {n} ✰", "✿ {n} ✿", "⚜ {n} ⚜", "✵ {n} ✵", "⟡ {n} ⟡", 
    "❃ {n} ❃", "♛ {n} ♛", "🎀 {n} 🎀", "🌙 {n} 🌙", "🌟 {n} 🌟"
]

def generate_designs(name):
    designs = set()
    
    # Generate Name variations
    names = {
        "bold": name.translate(FONTS["bold"]),
        "cursive": name.translate(FONTS["cursive"]),
        "gothic": name.translate(FONTS["gothic"]),
        "double": name.translate(FONTS["double"]),
        "smallcaps": name.translate(FONTS["smallcaps"]),
        "circle": name.translate(FONTS["circle"]),
        "square": name.upper().translate(FONTS["square"]),
        "fullwidth": name.translate(FONTS["fullwidth"])
    }

    # 1. Pure Fonts (Bina border ke)
    for font_name in names.values():
        designs.add(font_name)

    # 2. User's Exact Borders + Bold Font
    for border in USER_BORDERS:
        designs.add(border.format(n=names["bold"]))
        
    # 3. User's Exact Borders + SmallCaps Font
    for border in USER_BORDERS:
        designs.add(border.format(n=names["smallcaps"]))
        
    # 4. Auto Borders + Various Fonts
    for border in AUTO_BORDERS:
        designs.add(border.format(n=names["bold"]))
        designs.add(border.format(n=names["cursive"]))
        designs.add(border.format(n=names["gothic"]))
        designs.add(border.format(n=names["double"]))
        designs.add(border.format(n=names["smallcaps"]))
        designs.add(border.format(n=names["circle"]))
        
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

        status = await message.reply_text("✨ **Generating 400+ Premium Designs... Wait!**")
        
        results = generate_designs(text)
        
        # Send in chunks to prevent Telegram limits
        chunk = ""
        count = 1
        for res in results:
            if len(chunk) + len(res) > 3500:
                await message.reply_text(chunk, disable_web_page_preview=True)
                chunk = ""
                await asyncio.sleep(1)
            chunk += res + "\n\n"
            
        if chunk:
            await message.reply_text(chunk, disable_web_page_preview=True)
            
        await status.delete()
