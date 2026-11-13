# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# The exact heavy combining character
HEAVY_CHAR = "꯭"

def make_premium_font(text):
    bold = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bold_map = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    small = "abcdefghijklmnopqrstuvwxyz"
    small_map = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"

    result = HEAVY_CHAR * 7
    for i, char in enumerate(text):
        if char.isalpha():
            if i == 0:
                result += char.upper().translate(str.maketrans(bold, bold_map))
            else:
                result += char.lower().translate(str.maketrans(small, small_map))
        else:
            result += char
        
        # Add heavy characters after every letter
        result += HEAVY_CHAR * 7
        
    return result

# Exact 66 Borders you provided
BORDERS = [
    "❤️‍🔥 ⃪꯭⃝{n}👻𝆺꯭𝅥⎯꯭̽⎯꯭",
    "🦋⃤✺꯭⤹⌯꯭🫥꯭꯭𝆬{n}🌙꯭🐬᪵᪳𝄟",
    "꧁𓊈𒆜{n}𒆜𓊉꧂",
    "🍹𝆺𝅥⃝🤍⃪⃪꯭꯭㉿ ꯭͓{n}◡̈⃝🤍͕᪳𝆺꯭𝅥⎯꯭̽⎯꯭",
    "➳↡↡↡↡↡☬{n}☬↡↡↡↡↡➳",
    "✧⊹⊱⍣⊹⊱{n}⊹⊱⍣⊹⊰✧",
    "◄⏤͟͟͞ ⃪ͥ͢𐏓⃝⃪⭕ғͥғ𓆩{n}𓆪••➤‌‌",
    "𝄟͢ᶦ―ᷟ⃞᪵{n}𝄟⃝🤫᭄",
    "̶̶ ̶꯭͓̽♥️ ⃪꯭⃜{n}᭡፝֟፝֟͢🍃اا̽ـ꯭ــ꯭ـ⃛و꯭",
    "˟ ̶꯭⃖ ̶꯭꯭🪂⃪꯭⃝{n}𓆩🥵꯭𓆪",
    ".⎯꯭᪵᪳🦋⃝‌꯭𝅦𝅥𝅥ٖٖ͟͟͟͟𝄀𝄄𝄀꯭͟͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "◦•●◉✿ {n} ✿◉●•◦",
    "╰•★★ {n} ★★•╯",
    "❁⭒☆{n}☆⭒❁",
    "𓃭⃞⃔͢{n}➼ ᭄꯭꯭❥𝄄⃟꯭𝅥ͦ𝆬🥂",
    "𓆩𓆪𓆩𓆪❖{n}❖𓆩𓆪𓆩𓆪",
    "✪♕☬{n}☬♕✪",
    "⎯꯭̽ᬃ{n}🧸⎯",
    "⏤⃝⃪꯭⃮͙͙⃕⃔🌺⃪꯭͙͙𝆭{n}🤍⃪꯭͙͙⏤",
    "ミ★ {n} ★彡",
    "⫸⫷⫸⫷⫸✪{n}✪⫸⫷⫸⫷⫸",
    "──⃜͢͢៎꯭꯭꯭🐼⃪꯭͓͢°⃪꯭𝆺꯭𝅥{n} ꯭͢⃟͢🍒⛦⃕͜🍃",
    "꧁༒☬{n}☬༒꧂",
    "𝁘꯭ ꯭ྭ꯭{n}➛🕸",
    "꧁✿✿✿ {n} ✿✿✿꧂",
    "༺༒❁{n}❁༒༻",
    "𓄂≛⃝{n} ꯭𝅥ͦ𝆬🚭",
    "❘☞ͥ͟⋆ͣ͟⋆ͫ⍣{n}⍣❘꯭𝄄꯭",
    "꧁•⊹٭{n}٭⊹•꧂",
    "个『{n}』个",
    ".⎯᪵᪵፝֟፝֟⎯꯭𝄀𝄄𝄀🌸꯭꯭͟{n}🦋",
    "⎯͢ꠋ ᶦϻͣ། ⃪ͥ͢ 🌺͜͟{n}🫧",
    "𒆜꯭•☬•꯭{n}•☬•꯭𒜜",
    "✤𖠌𓂀✤ {n} ✤𓂀𖠌✤",
    "˚₊·𐏓꯭ᶜᵘᵗᵉ {n}°‌🥀",
    "ıllıllı⭐🌟 {n} 🌟⭐ıllıllı",
    "◄🕊️⃪꯭̽͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "ᯓ🩺̶̶᪵˟̶ 𝆺𝅥⃝🫀{n}ﮩ᪵٨ـﮩ➛♥️",
    "⋆⋆⋆❀{n}❀⋆⋆⋆",
    "•─┼ᶦϻ‌།͢ ⃪{n}🍓꯭᪳᪼᪳",
    "亗『{n}』亗",
    "◄⏤͟͟͞🤍⃝⃪🦋⃪꯭ᵛ̲ᵎ̲ᵖ̲𒉜{n}🌸︭︫┼⁰⁰⁷─⦁••",
    "°†° «[{n}]» °†°",
    "☆☬{n}☬☆",
    "⎯⃛㬓𓆩⃗㬓͟🍃̶̌͟🅼ɨֆֆ𝆺𝅥⃝{n}˶֟፝͟͝⎯꯭̽ 🖤",
    "🥀 ⃪ͥ͢ ᷟ𝆺꯭꯭𝅥᪳‌{n} ⎯꯭꯭᪵᪵፝֟፝❤️‍🔥",
    "➶➶➶➶➶⫷{n}⫸➶➶➶➶➶",
    "★¸.•☆•.¸★ {n} ★⡀.•☆•.★",
    "➤⇌⇌⇌{n}⇌⇌⇌➤",
    "❖꯭𓂀⃝{n}𓂀⃝꯭❖",
    "【★】➳✮{n}✮➳【★】",
    "❥⃝⍣{n}❥⃝⍣",
    "⛥꯭ᴳᴼᴰ⛥꯭{n}⛥꯭",
    "🝐꯭𓆩꯭꯭⍣⃪{n}⃪⍣꯭꯭𓆪꯭🝐",
    "◄❥ ⃝⃪⃕♥️̶⍣⃪͜🌿𝄄᭄{n}🍃⃝🎸",
    "◄⏤͟͞ꭙ𝆺𝅥⃝🔥 ⃪ͥ͢{n}༎ࠫ⛧‌ٖٖٖٖٖٖٜٖٖٖٖ𝆺꯭𝅥🤍",
    "☔️⃟⃚⃐⎯⃚꯭፝֟֗. ⃝{n}✿⃟☔️✾",
    "★彡[{n}]彡★",
    "𓄂꯭꯭‌≛⃝꯭{n}𐎭❥┼🕊️",
    "✿્᭄͜͡⃝❥{n}༏༏𝆺꯭𝅥𝆺꯭𝅥༎ࠫ✿͜͡࿐",
    "•⏤‌𝄞⃝🍧 ‌⃪‌{n}♥️꯭꯭꯭꯭ ꯭꯭᪳𝆺𝅥",
    "⎯ᷝ⎯ⷨ͢ {n}𝆺꯭𝅥❤️‍🔥⎯꯭ͯ⟶⋆",
    "──⃜͢͢🥤⃘⃝⃟⃪⃜{n}༎͢🦋",
    "⤹ ⃪{n} ⃪🤭꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭",
    "⋆⎯꯭̽𝅃꯭᳚{n}𝅃꯭꯭᳚ ⃪꯭⃝𐏓꯭",
    "𓂀 {n} 𓂀"
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

        status = await message.reply_text("✨ **Generating Ultra Premium Aesthetic Designs...**")
        
        premium_name = make_premium_font(text)
        
        results = []
        for border in BORDERS:
            results.append(border.format(n=premium_name))
            
        # Send in chunks to avoid Telegram limits
        chunk = ""
        for res in results:
            if len(chunk) + len(res) > 3500:
                await message.reply_text(chunk, disable_web_page_preview=True)
                chunk = ""
                await asyncio.sleep(1)
            chunk += res + "\n\n"
            
        if chunk:
            await message.reply_text(chunk, disable_web_page_preview=True)
            
        await status.delete()
