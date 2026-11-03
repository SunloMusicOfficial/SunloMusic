import os, math, random
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from pyrogram.enums import ButtonStyle
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

# ✅ 15+ Advanced Unicode Fonts
FONTS = {
    "𝗕𝗼𝗹𝗱": {c: chr(ord(c) + 0x1D5D4 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5EE - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"},
    "𝑰𝒕𝒂𝒍𝒊𝒄": {c: chr(ord(c) + 0x1D608 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D622 - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"},
    "𝓢𝓬𝓻𝓲𝓹𝓽": {c: chr(ord(c) + 0x1D49C - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D4B6 - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"},
    "𝕯𝖔𝖚𝖇𝖑𝖊": {c: chr(ord(c) + 0x1D538 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D552 - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"},
    "𝔉𝔯𝔞𝔨𝔱𝔲𝔯": {c: chr(ord(c) + 0x1D504 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D51E - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"},
    "𝙼𝚘𝚗𝚘": {c: chr(ord(c) + 0x1D670 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D68A - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"},
    "Ｆｕｌｌ": {c: chr(ord(c) + 0xFF21 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0xFF41 - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"},
    "ᴄᴀᴘꜱ": {c: chr(ord(c) + 0x1D00) if 'A' <= c <= 'Z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    "Bᴜʙʙʟᴇ": {c: chr(ord(c) + 0x24B6 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x24D0 - 97) if 'a' <= c <= 'z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"},
    "Sqᴜᴀʀᴇ": {c: chr(ord(c) + 0x1F130 - 65) if 'A' <= c <= 'Z' else c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
}

# ✅ 150+ Premium Wrappers
WRAPPERS = [
    ("✿્᭄͡", "ᥫ᭡፝֟፝֟"), ("꧁༒☬", "☬༒꧂"), ("༒⚔◥", "◤⚔༒"), ("╰☆☆", "☆☆╮"),
    ("•´¯`•.", ".•´¯`•"), ("♡", "♡"), ("𓆩", "𓆪"), ("『", "』"), ("▰▱▰", "▰▱▰"),
    ("✧･ﾟ: *✧", "✧*:･ﾟ✧"), ("⋆｡°✩", "✩°｡⋆"), ("▄︻デ══━一", ""), ("⚡▬▬▬▬", "▬▬▬▬⚡"),
    ("🍃", "🍃"), ("🔥", "🔥"), ("👑", "👑"), ("🎸", "🎸"), ("⚜️", "⚜️"),
    ("✨", "✨"), ("🖤", "🖤"), ("💎", "💎"), ("🌙", "🌙"), ("☀️", "☀️"),
    ("⚡", "⚡"), ("🍷", "🍷"), ("🕊️", "🕊️"), ("🦋", "🦋"), ("🌸", "🌸"),
    ("⋆", "⋆"), ("✧", "✧"), ("❥", "❥"), ("➳", "➳"), ("☬", "☬"),
    ("༺", "༻"), ("༼", "༽"), ("【", "】"), ("《", "》"), ("〔", "〕"),
    ("╭", "╮"), ("╰", "╯"), ("┏", "┓"), ("┗", "┛"), ("┣", "┫"),
    ("◥", "◤"), ("◢", "◣"), ("▰", "▰"), ("▱", "▱"), ("◆", "◆"),
    ("◇", "◇"), ("◈", "◈"), ("❖", "❖"), ("✹", "✹"), ("✺", "✺"),
    ("✵", "✵"), ("✶", "✶"), ("✷", "✷"), ("✸", "✸"), ("✹", "✹"),
    ("⚘", "⚘"), ("⚚", "⚚"), ("⚝", "⚝"), ("⚞", "⚟"), ("⛧", "⛧"),
    ("☥", "☥"), ("☬", "☬"), ("☯", "☯"), ("♆", "♆"), ("♨", "♨"),
    ("⚔️", "⚔️"), ("🛡️", "🛡️"), ("🗡️", "🗡️"), ("🏹", "🏹"), ("🔱", "🔱"),
    ("🎧", "🎧"), ("🎤", "🎤"), ("🎼", "🎼"), ("🎹", "🎹"), ("🥁", "🥁"),
    ("⭐", "⭐"), ("🌟", "🌟"), ("💫", "💫"), ("🌠", "🌠"), ("☄️", "☄️"),
    ("🌪️", "🌪️"), ("🌊", "🌊"), ("🏔️", "🏔️"), ("🌋", "🌋"), ("🌌", "🌌"),
    ("🍁", "🍁"), ("🍂", "🍂"), ("🌿", "🌿"), ("☘️", "☘️"), ("🍀", "🍀"),
    ("🌹", "🌹"), ("🥀", "🥀"), ("🌺", "🌺"), ("🌻", "🌻"), ("🌼", "🌼"),
    ("🦅", "🦅"), ("🦁", "🦁"), ("🐉", "🐉"), ("🦄", "🦄"), ("🐺", "🐺"),
    ("👾", "👾"), ("👽", "👽"), ("🤖", "🤖"), ("💀", "💀"), ("☠️", "☠️"),
    ("👻", "👻"), ("😈", "😈"), ("👿", "👿"), ("🤍", "🤍"), ("💙", "💙"),
    ("💚", "💚"), ("💛", "💛"), ("🧡", "🧡"), ("❤️", "❤️"), ("💜", "💜"),
    ("🖤", "🖤"), ("🤎", "🤎"), ("💔", "💔"), ("❣️", "❣️"), ("💕", "💕"),
    ("║▌│█│║▌║", "║▌│█│║▌║"), ("[̲̅", "̲̅]"), ("⫷", "⫸"), ("⚡", "⚡"),
    ("꧁", "꧂"), ("♛", "♛"), ("⚜", "⚜"), ("༄", "༄"), ("⁀➷", "")
]

def apply_font(text: str, font_map: dict) -> str:
    return "".join(font_map.get(c, c) for c in text)

def generate_styles(name: str) -> list:
    styles = []
    
    # 1. Font Variations (Plain)
    for font_name, mapping in FONTS.items():
        styles.append(apply_font(name, mapping))
        
    # 2. Font Variations with Wrappers (Massive Combinations)
    for font_name, mapping in FONTS.items():
        styled_name = apply_font(name, mapping)
        for pre, suf in WRAPPERS:
            styles.append(f"{pre} {styled_name} {suf}")
            
    # 3. Normal Name with Wrappers
    for pre, suf in WRAPPERS:
        styles.append(f"{pre} {name} {suf}")
        
    # 4. Special Zalgo / Cursed Text (Randomized)
    for _ in range(10):
        zalgo_name = "".join([c + "".join([chr(random.randint(0x0300, 0x036F)) for _ in range(2)]) for c in name])
        styles.append(f"☠️ {zalgo_name} ☠️")

    # Remove duplicates and shuffle slightly to mix fonts
    unique_styles = list(dict.fromkeys(styles))
    random.shuffle(unique_styles)
    return unique_styles

# ✅ In-Memory Cache for Pagination
STYLE_CACHE = {}

@bot.on_message(filters.command(["style", "font", "stylize"]))
@catch_errors
async def style_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/style YourName</code>\n<i>Example: /style Sakil</i>")
        
    name = " ".join(m.command[1:])
    if len(name) > 20:
        return await m.reply_text("❌ <b>Name is too long!</b> Please keep it under 20 characters.")
        
    status = await m.reply_text(f"✨ <b>Generating Premium Designs for</b> <code>{name}</code>...")
    
    try:
        styles = generate_styles(name)
        STYLE_CACHE[m.from_user.id] = {"name": name, "styles": styles}
        
        # Show page 1
        await send_style_page(status, m.from_user.id, page=1, is_edit=False)
            
    except Exception as e:
        LOGGER.error(f"Styler Error: {e}")
        await status.edit_text(f"❌ <b>Failed to generate designs:</b> <code>{e}</code>")

async def send_style_page(message_obj, user_id: int, page: int, is_edit: bool = True):
    data = STYLE_CACHE.get(user_id)
    if not data:
        return
        
    styles = data["styles"]
    name = data["name"]
    
    items_per_page = 25
    total_pages = math.ceil(len(styles) / items_per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_styles = styles[start_idx:end_idx]
    
    # Formatting the Premium Card
    text = (
        f"✨ <b>『 ᴘʀᴇᴍɪᴜᴍ ꜱᴛʏʟᴇꜱ 』</b> ✨\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👤 <b>Name:</b> <code>{name}</code>\n"
        f"🎨 <b>Total Designs:</b> <code>{len(styles)}</code>\n"
        f"📄 <b>Page:</b> <code>{page}/{total_pages}</code>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👇 <i>Tap on any design to copy it!</i>\n\n"
    )
    
    for i, style in enumerate(page_styles, 1):
        text += f"{start_idx + i}. <code>{style}</code>\n"
        
    # Pagination Buttons
    buttons = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ ᴘʀᴇᴠ", callback_data=f"style_page_{user_id}_{page-1}", style=ButtonStyle.PRIMARY))
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="style_ignore", style=ButtonStyle.SUCCESS))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"style_page_{user_id}_{page+1}", style=ButtonStyle.PRIMARY))
        
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data=f"style_close_{user_id}", style=ButtonStyle.DANGER)])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if is_edit:
        try:
            await message_obj.edit_text(text, reply_markup=reply_markup, link_preview_options=LinkPreviewOptions(is_disabled=True))
        except:
            pass
    else:
        try:
            await message_obj.edit_text(text, reply_markup=reply_markup, link_preview_options=LinkPreviewOptions(is_disabled=True))
        except:
            await message_obj.delete()
            await bot.send_message(message_obj.chat.id, text, reply_markup=reply_markup, link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex(r"^style_page_"))
@catch_errors
async def style_pagination_cb(_, cq: CallbackQuery):
    _, _, user_id, page = cq.data.split("_")
    user_id = int(user_id)
    page = int(page)
    
    if cq.from_user.id != user_id:
        return await cq.answer("🚫 Ye tumhare liye nahi hai! /style command use karo.", show_alert=True)
        
    await send_style_page(cq.message, user_id, page, is_edit=True)
    await cq.answer()

@bot.on_callback_query(filters.regex(r"^style_ignore$"))
@catch_errors
async def style_ignore_cb(_, cq: CallbackQuery):
    await cq.answer("Ye page number hai. Aage jaane ke liye 'Next' dabao.", show_alert=False)

@bot.on_callback_query(filters.regex(r"^style_close_"))
@catch_errors
async def style_close_cb(_, cq: CallbackQuery):
    _, _, user_id = cq.data.split("_")
    if cq.from_user.id != int(user_id):
        return await cq.answer("🚫 Ye tumhare liye nahi hai!", show_alert=True)
        
    STYLE_CACHE.pop(int(user_id), None)
    await cq.message.delete()
    await cq.answer("Closed!")
