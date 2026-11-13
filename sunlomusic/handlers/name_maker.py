# Copyright (C) @YO_UR_OFFICIAL_CRUSH
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from pyrogram.errors import MessageNotModified
import math

RESULTS_CACHE = {}

# 1. Premium Fonts Map
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

# 2. User's 66 Borders (Removed trailing Zalgo char to prevent lines)
USER_BORDERS = [
    "❤️‍🔥 ⃪꯭⃝{n}👻𝆺꯭𝅥⎯꯭̽⎯", "🦋⃤✺꯭⤹⌯꯭🫥꯭𝆬{n}🌙꯭🐬᪵᪳𝄟",
    "꧁𓊈𒆜{n}𒆜𓊉꧂", "🍹𝆺𝅥⃝🤍⃪⃪꯭꯭㉿ ꯭͓{n}◡̈⃝🤍͕᪳𝆺꯭𝅥⎯꯭̽⎯",
    "➳↡↡↡↡↡☬{n}☬↡↡↡↡↡➳", "✧⊹⊱⍣⊹⊱{n}⊹⊱⍣⊹⊰✧",
    "◄⏤͟͟͞ ⃪ͥ͢𐏓⃝⃪⭕ғͥғ𓆩{n}𓆪••➤‌‌", "𝄟͢ᶦ―ᷟ⃞᪵{n}𝄟⃝🤫᭄",
    "̶̶ ̶꯭͓̽♥️ ⃪꯭⃜{n}᭡፝֟፝֟͢🍃اا̽ـ꯭ــ꯭ـ⃛و", "˟ ̶꯭⃖ ̶꯭꯭🪂⃪꯭⃝{n}𓆩🥵꯭𓆪",
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
    "【★】➳✮{n}✮➳【★】", "❥⃝⍣{n}❥⃝⍣", "⛥꯭ᴳᴼᴰ⛥꯭{n}⛥",
    "🝐꯭𓆩꯭꯭⍣⃪{n}⃪⍣꯭꯭𓆪꯭🝐", "◄❥ ⃝⃪⃕♥️̶⍣⃪͜🌿𝄄᭄{n}🍃⃝🎸",
    "◄⏤͟͞ꭙ𝆺𝅥⃝🔥 ⃪ͥ͢{n}༎ࠫ⛧‌ٖٖٖٖٖٖٜٖٖٖٖ𝆺꯭𝅥🤍", "☔️⃟⃚⃐⎯⃚꯭፝֟֗. ⃝{n}✿⃟☔️✾",
    "★彡[{n}]彡★", "𓄂꯭꯭‌≛⃝꯭꯭꯭‌{n}𐎭❥┼🕊️", "✿્᭄͜͡⃝❥{n}༏༏𝆺꯭𝅥𝆺꯭𝅥༎ࠫ✿͜͡࿐",
    "•⏤‌𝄞⃝🍧 ‌⃪‌{n}♥️꯭꯭꯭꯭ ꯭꯭᪳𝆺𝅥", "⎯ᷝ⎯ⷨ͢ {n}𝆺꯭𝅥❤️‍🔥⎯꯭ͯ⟶⋆",
    "──⃜͢͢🥤⃘⃝⃟⃪⃜{n}༎͢🦋", "⤹ ⃪{n} ⃪🤭꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯", "⋆⎯꯭̽𝅃꯭᳚{n}𝅃꯭꯭᳚ ⃪꯭⃝𐏓", "𓂀 {n} 𓂀"
]

def generate_designs(name):
    designs = []
    
    # Generate combinations of Fonts and Borders
    for font_name, trans_map in FONTS.items():
        styled_name = name.translate(trans_map)
        
        # Pure Font (No Border)
        designs.append(styled_name)
        
        # Font + All Borders
        for border in USER_BORDERS:
            designs.append(border.format(n=styled_name))
            
    return designs

def get_page_markup(user_id, page, total_pages):
    buttons = []
    prev_btn = InlineKeyboardButton("⬅️ Prev", callback_data=f"nm_{user_id}_{page-1}" if page > 0 else "nm_ignore", style=ButtonStyle.PRIMARY)
    page_btn = InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="nm_ignore", style=ButtonStyle.DANGER)
    next_btn = InlineKeyboardButton("Next ➡️", callback_data=f"nm_{user_id}_{page+1}" if page < total_pages - 1 else "nm_ignore", style=ButtonStyle.SUCCESS)
    buttons.append(prev_btn)
    buttons.append(page_btn)
    buttons.append(next_btn)
    return InlineKeyboardMarkup([buttons])

def register_name_maker(app: Client):
    @app.on_message(filters.command("name"))
    async def name_command(client, message: Message):
        text = ""
        if len(message.text.split()) > 1:
            text = message.text.split(maxsplit=1)[1].strip()
        elif message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text.strip()
            
        if not text:
            await message.reply_text("**Usage:**\n`/name Sakil` \nYa kisi ke message par reply karke `/name` likhein.")
            return
            
        if len(text) > 15:
            await message.reply_text("**Name is too long! Max 15 chars.**")
            return

        status = await message.reply_text("✨ **Generating 500+ Premium Designs...**")
        
        designs = generate_designs(text)
        user_id = message.from_user.id
        RESULTS_CACHE[user_id] = (text, designs)
        
        items_per_page = 20
        total_pages = math.ceil(len(designs) / items_per_page)
        
        first_page_items = designs[0:items_per_page]
        page_text = f"✨ **Premium Name Styles for** `{text}` ✨\n\n👇 **Tap on any style to copy:**\n\n"
        for item in first_page_items:
            page_text += f"`{item}`\n\n"
            
        markup = get_page_markup(user_id, 0, total_pages)
        await status.edit_text(page_text, reply_markup=markup)

    @app.on_callback_query(filters.regex(r"^nm_"), group=-1)
    async def name_callback(client, callback_query):
        await callback_query.answer()
        data = callback_query.data.split("_")
        
        if data[1] == "ignore":
            return
            
        user_id = int(data[1])
        page = int(data[2])
        
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ Yeh buttons aapke liye nahi hain.", show_alert=True)
            return
            
        cached_data = RESULTS_CACHE.get(user_id)
        if not cached_data:
            await callback_query.answer("⏳ Session expired. Please /name dobara likhein.", show_alert=True)
            return
            
        text, designs = cached_data
        items_per_page = 20
        total_pages = math.ceil(len(designs) / items_per_page)
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = designs[start_idx:end_idx]
        
        page_text = f"✨ **Premium Name Styles for** `{text}` ✨\n\n👇 **Tap on any style to copy:**\n\n"
        for item in page_items:
            page_text += f"`{item}`\n\n"
            
        markup = get_page_markup(user_id, page, total_pages)
        try:
            await callback_query.message.edit_text(page_text, reply_markup=markup)
        except MessageNotModified:
            pass
