# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
import math

# Cache to store generated names temporarily
RESULTS_CACHE = {}

# Zalgo Effect Generator
HEAVY_CHAR = "꯭"

def make_zalgo(text):
    bold = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bold_map = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    small = "abcdefghijklmnopqrstuvwxyz"
    small_map = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    
    result = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i == 0:
                result += char.upper().translate(str.maketrans(bold, bold_map))
            else:
                result += char.lower().translate(str.maketrans(small, small_map))
        else:
            result += char
        result += HEAVY_CHAR * 7
    return result

# User's Exact 66 Borders
USER_BORDERS = [
    "❤️‍🔥 ⃪꯭⃝{n}👻𝆺꯭𝅥⎯꯭̽⎯꯭", "🦋⃤✺꯭⤹⌯꯭🫥꯭꯭꯭꯭꯭꯭꯭꯭𝆬{n}🌙꯭🐬᪵᪳𝄟",
    "꧁𓊈𒆜{n}𒆜𓊉꧂", "🍹𝆺𝅥⃝🤍⃪⃪꯭꯭㉿ ꯭͓{n}◡̈⃝🤍͕᪳𝆺꯭𝅥⎯꯭̽⎯꯭",
    "➳↡↡↡↡↡☬{n}☬↡↡↡↡↡➳", "✧⊹⊱⍣⊹⊱{n}⊹⊱⍣⊹⊰✧",
    "◄⏤͟͟͞ ⃪ͥ͢𐏓⃝⃪⭕ғͥғ𓆩{n}𓆪••➤‌‌", "𝄟͢ᶦ―ᷟ⃞᪵{n}𝄟⃝🤫᭄",
    "̶̶ ̶꯭͓̽♥️ ⃪꯭⃜{n}᭡፝֟፝֟͢🍃اا̽ـ꯭ــ꯭ـ⃛و꯭", "˟ ̶꯭⃖ ̶꯭꯭🪂⃪꯭⃝{n}𓆩🥵꯭𓆪",
    ".⎯꯭᪵᪳🦋⃝‌꯭𝅦𝅥𝅥ٖٖ͟͟͟͟𝄀𝄄𝄀꯭͟͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "◦•●◉✿ {n} ✿◉●•◦", "╰•★★ {n} ★★•╯", "❁⭒☆{n}☆⭒❁",
    "𓃭⃞⃔͢{n}➼ ᭄꯭꯭❥𝄄⃟꯭𝅥ͦ𝆬🥂", "𓆩𓆪𓆩𓆪❖{n}❖𓆩𓆪𓆩𓆪", "✪♕☬{n}☬♕✪",
    "⎯꯭̽ᬃ{n}🧸⎯", "⏤⃝⃪꯭⃮͙͙⃕⃔🌺⃪꯭͙͙𝆭{n}🤍⃪꯭͙͙⏤", "ミ★ {n} ★彡",
    "⫸⫷⫸⫷⫸✪{n}✪⫸⫷⫸⫷⫸", "──⃜͢͢៎꯭꯭꯭🐼⃪꯭͓͢°⃪꯭𝆺꯭𝅥{n} ꯭͢⃟͢🍒⛦⃕͜🍃",
    "꧁༒☬{n}☬༒꧂", "𝁘꯭ ꯭ྭ꯭{n}➛🕸", "꧁✿✿✿ {n} ✿✿✿꧂", "༺༒❁{n}❁༒༻",
    "𓄂≛⃝{n} ꯭𝅥ͦ𝆬🚭", "❘☞ͥ͟⋆ͣ͟⋆ͫ⍣{n}⍣❘꯭𝄄꯭", "꧁•⊹٭{n}٭⊹•꧂", "个『{n}』个",
    ".⎯᪵᪵፝֟፝֟⎯꯭𝄀𝄄𝄀🌸꯭꯭͟{n}🦋", "⎯͢ꠋ ᶦϻͣ། ⃪ͥ͢ 🌺͜͟{n}🫧",
    "𒆜꯭•☬•꯭{n}•☬•꯭𒆜", "✤𖠌𓂀✤ {n} ✤𓂀𖠌✤", "˚₊·𐏓꯭ᶜᵘᵗᵉ {n}°‌🥀",
    "ıllıllı⭐🌟 {n} 🌟⭐ıllıllı", "◄🕊️⃪꯭̽͟{n}🦋⃝‌ٖٖٖٖ ‌ٖٖٖٖٖ❤️‍🔥",
    "ᯓ🩺̶̶᪵˟̶ 𝆺𝅥⃝🫀{n}ﮩ᪵٨ـﮩ➛♥️", "⋆⋆⋆❀{n}❀⋆⋆⋆",
    "•─┼ᶦϻ‌།͢ ⃪{n}🍓꯭᪳᪼᪳", "亗『{n}』亗",
    "◄⏤͟͟͞🤍⃝⃪🦋⃪꯭ᵛ̲ᵎ̲ᵖ̲𒉜{n}🌸︭︫┼⁰⁰⁷─⦁••", "°†° «[{n}]» °†°",
    "☆☬{n}☬☆", "⎯⃛㬓𓆩⃗㬓͟🍃̶̌͟🅼ɨֆֆ𝆺𝅥⃝{n}˶֟፝͟͝⎯꯭̽ 🖤",
    "🥀 ⃪ͥ͢ ᷟ𝆺꯭꯭𝅥᪳‌{n} ⎯꯭꯭᪵᪵፝֟፝❤️‍🔥", "➶➶➶➶➶⫷{n}⫸➶➶➶➶➶",
    "★¸.•☆•.¸★ {n} ★⡀.•☆•.★", "➤⇌⇌⇌{n}⇌⇌⇌➤", "❖꯭𓂀⃝{n}𓂀⃝꯭❖",
    "【★】➳✮{n}✮➳【★】", "❥⃝⍣{n}❥⃝⍣", "⛥꯭ᴳᴼᴰ⛥꯭{n}⛥꯭",
    "🝐꯭𓆩꯭꯭⍣⃪{n}⃪⍣꯭꯭𓆪꯭🝐", "◄❥ ⃝⃪⃕♥️̶⍣⃪͜🌿𝄄᭄{n}🍃⃝🎸",
    "◄⏤͟͞ꭙ𝆺𝅥⃝🔥 ⃪ͥ͢{n}༎ࠫ⛧‌ٖٖٖٖٖٖٜٖٖٖٖ𝆺꯭𝅥🤍", "☔️⃟⃚⃐⎯⃚꯭፝֟֗. ⃝{n}✿⃟☔️✾",
    "★彡[{n}]彡★", "𓄂꯭꯭‌≛⃝꯭꯭꯭‌{n}𐎭❥┼🕊️", "✿્᭄͜͡⃝❥{n}༏༏𝆺꯭𝅥𝆺꯭𝅥༎ࠫ✿͜͡࿐",
    "•⏤‌𝄞⃝🍧 ‌⃪‌{n}♥️꯭꯭꯭꯭ ꯭꯭᪳𝆺𝅥", "⎯ᷝ⎯ⷨ͢ {n}𝆺꯭𝅥❤️‍🔥⎯꯭ͯ⟶⋆",
    "──⃜͢͢🥤⃘⃝⃟⃪⃜{n}༎͢🦋", "⤹ ⃪{n} ⃪🤭꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭", "⋆⎯꯭̽𝅃꯭᳚{n}𝅃꯭꯭᳚ ⃪꯭⃝𐏓꯭", "𓂀 {n} 𓂀"
]

def generate_designs(name):
    designs = []
    zalgo_name = make_zalgo(name)
    
    for border in USER_BORDERS:
        designs.append(border.format(n=zalgo_name))
        
    return designs

def get_page_markup(user_id, page, total_pages):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"nm_{user_id}_{page-1}"))
    else:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data="nm_ignore"))
        
    buttons.append(InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="nm_ignore"))
    
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"nm_{user_id}_{page+1}"))
    else:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data="nm_ignore"))
        
    return InlineKeyboardMarkup([buttons])

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

        status = await message.reply_text("✨ **Generating Premium Zalgo Designs...**")
        
        designs = generate_designs(text)
        user_id = message.from_user.id
        
        # Cache save: storing tuple of (name, designs)
        RESULTS_CACHE[user_id] = (text, designs)
        
        items_per_page = 8
        total_pages = math.ceil(len(designs) / items_per_page)
        
        first_page_items = designs[0:items_per_page]
        page_text = "✨ **Premium Name Styles for** `" + text + "` ✨\n\n" + "\n\n".join(first_page_items)
        markup = get_page_markup(user_id, 0, total_pages)
        
        await status.edit_text(page_text, reply_markup=markup)

    @app.on_callback_query(filters.regex(r"^nm_"))
    async def name_callback(client, callback_query):
        data = callback_query.data.split("_")
        
        if data[1] == "ignore":
            await callback_query.answer("Yeh sirf page number hai.")
            return
            
        user_id = int(data[1])
        page = int(data[2])
        
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ Yeh buttons aapke liye nahi hain. Apna khud ka /name command use karein.", show_alert=True)
            return
            
        cached_data = RESULTS_CACHE.get(user_id)
        if not cached_data:
            await callback_query.answer("Session expired. Please use /name again.", show_alert=True)
            return
            
        text, designs = cached_data
        items_per_page = 8
        total_pages = math.ceil(len(designs) / items_per_page)
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        
        page_items = designs[start_idx:end_idx]
        page_text = "✨ **Premium Name Styles for** `" + text + "` ✨\n\n" + "\n\n".join(page_items)
        markup = get_page_markup(user_id, page, total_pages)
        
        try:
            await callback_query.message.edit_text(page_text, reply_markup=markup)
            await callback_query.answer()
        except MessageNotModified:
            await callback_query.answer()
        except Exception as e:
            await callback_query.answer(f"Error: {e}", show_alert=True)
