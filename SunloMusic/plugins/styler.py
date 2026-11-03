import os, math, random
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from pyrogram.enums import ButtonStyle
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

# ✅ 18+ Advanced Unicode Fonts (Including Regional & Small Caps)
FONTS = {
    "𝗕𝗼𝗹𝗱": lambda s: "".join(chr(ord(c) + 0x1D5D4 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5EE - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝑰𝒕𝒂𝒍𝒊𝒄": lambda s: "".join(chr(ord(c) + 0x1D608 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D622 - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝓢𝓬𝓻𝓲𝓹𝓽": lambda s: "".join(chr(ord(c) + 0x1D49C - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D4B6 - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝕯𝖔𝖚𝖇𝖑𝖊": lambda s: "".join(chr(ord(c) + 0x1D538 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D552 - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝔉𝔯𝔞𝔨𝔱𝔲𝔯": lambda s: "".join(chr(ord(c) + 0x1D504 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D51E - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝙼𝚘𝚗𝚘": lambda s: "".join(chr(ord(c) + 0x1D670 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D68A - 97) if 'a' <= c <= 'z' else c for c in s),
    "Ｆｕｌｌ": lambda s: "".join(chr(ord(c) + 0xFF21 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0xFF41 - 97) if 'a' <= c <= 'z' else c for c in s),
    "ᴄᴀᴘꜱ": lambda s: "".join(chr(ord(c) + 0x1D00) if 'A' <= c <= 'Z' else c for c in s),
    "𝐒𝐞𝐫𝐢𝐟": lambda s: "".join(chr(ord(c) + 0x1D400 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D41A - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝕾𝖆𝖓𝖘": lambda s: "".join(chr(ord(c) + 0x1D5A0 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5BA - 97) if 'a' <= c <= 'z' else c for c in s),
    "Ⓒⓘⓡⓒⓛⓔ": lambda s: "".join(chr(ord(c) + 0x24B6 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x24D0 - 97) if 'a' <= c <= 'z' else c for c in s),
    "🄢🄠🄟": lambda s: "".join(chr(ord(c) + 0x1F130 - 65) if 'A' <= c <= 'Z' else c for c in s),
    "🇷ᴇɢɪᴏɴᴀʟ": lambda s: "".join(chr(ord(c) + 0x1F1E6 - 65) if 'A' <= c <= 'Z' else c for c in s),
    "𝕭𝖔𝖑𝖉 𝕱𝖗𝖆𝖐": lambda s: "".join(chr(ord(c) + 0x1D56C - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D586 - 97) if 'a' <= c <= 'z' else c for c in s),
    "𝑀𝒶𝓉𝒽": lambda s: "".join(chr(ord(c) + 0x1D434 - 65) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D44E - 97) if 'a' <= c <= 'z' else c for c in s),
    "ᴛɪɴʏ": lambda s: "".join(chr(ord(c) + 0x1D00) if 'A' <= c <= 'Z' else c for c in s),
    "🅑🅛🅞🅒🅚": lambda s: "".join(chr(ord(c) + 0x1F150 - 65) if 'A' <= c <= 'Z' else c for c in s),
    "Ⓝⓔⓖⓐⓣⓘⓥⓔ": lambda s: "".join(chr(ord(c) + 0x1F150 - 65) if 'A' <= c <= 'Z' else c for c in s),
}

# ✅ 150+ Heavy Aesthetic Frames (Derived from your examples)
FRAMES = [
    "✿્᭄͡ {} ᥫ᭡፝֟፝֟", "꧁༒☬{}☬༒꧂", "༒⚔◥ {} ◤⚔༒", "╰☆☆ {} ☆☆╮",
    "•´¯`•. {} .•´¯`•", "♡ {} ♡", "𓆩 {} 𓆪", "『 {} 』", "▰▱▰ {} ▰▱▰",
    "✧･ﾟ: *✧ {} ✧*:･ﾟ✧", "⋆｡°✩ {} ✩°｡⋆", "▄︻デ══━一 {}", "⚡▬▬▬▬ {} ▬▬▬▬⚡",
    "─╼⃝𖠁{}𖠁⃝╾─•", "⃝🌸𓆩{}𓆪⃟👑", "ᶜᵘᵗᵉ།{}͠", "○༄ {} •》👑", "♡ {} ♡",
    "🕊️⃝‌❥┽✖ᶦᶰᵈ᭄༺{}༻♕❤", "👑⃟🕊≛⃝{} ≛⃝🕊👑⃟", "𝄞ꠋꠋꠋ┼𝆺𝅥⃝ᶦϻ‌ᵛ‌ᵎᵖ ≛⃝❥︎︎𓆩{}𓆪≛⃝❥︎︎𖣔ꠋꠋꠋ",
    "─⃝➤ {}", "╰┈➤ {}", "⫸ {} ⫷", "➳ {} ➳", "☬ {} ☬", "༺ {} ༻", "༼ {} ༽", "【 {} 】", "《 {} 》", "〔 {} 〕",
    "╭ {} ╮", "╰ {} ╯", "┏ {} ┓", "┗ {} ┛", "▰ {} ▰", "◥ {} ◤", "◢ {} ◣", "◆ {} ◆", "❖ {} ❖", "✹ {} ✹",
    "✵ {} ✵", "✶ {} ✶", "✷ {} ✷", "✸ {} ✸", "⚘ {} ⚘", "⚚ {} ⚚", "⚝ {} ⚝", "⛧ {} ⛧", "☥ {} ☥", "☯ {} ☯",
    "♆ {} ♆", "⚔️ {} ⚔️", "🛡️ {} 🛡️", "🗡️ {} 🗡️", "🔱 {} 🔱", "🎧 {} 🎧", "🎤 {} 🎤", "🎼 {} 🎼", "🎹 {} 🎹",
    "🥁 {} 🥁", "⭐ {} ⭐", "🌟 {} 🌟", "💫 {} 💫", "🌠 {} 🌠", "☄️ {} ☄️", "🌪️ {} 🌪️", "🌊 {} 🌊", "🏔️ {} 🏔️",
    "🌋 {} 🌋", "🌌 {} 🌌", "🍁 {} 🍁", "🍂 {} 🍂", "🌿 {} 🌿", "☘️ {} ☘️", "🍀 {} 🍀", "🌹 {} 🌹", "🥀 {} 🥀",
    "🌺 {} 🌺", "🌻 {} 🌻", "🌼 {} 🌼", "🦅 {} 🦅", "🦁 {} 🦁", "🐉 {} 🐉", "🦄 {} 🦄", "🐺 {} 🐺", "👾 {} 👾",
    "👽 {} 👽", "🤖 {} 🤖", "💀 {} 💀", "☠️ {} ☠️", "👻 {} 👻", "😈 {} 😈", "👿 {} 👿", "💙 {} 💙", "💚 {} 💚",
    "💛 {} 💛", "🧡 {} 🧡", "❤️ {} ❤️", "💜 {} 💜", "🖤 {} 🖤", "🤎 {} 🤎", "💔 {} 💔", "❣️ {} ❣️", "💕 {} 💕",
    "║▌│█│║▌║ {} ║▌│█│║▌║", "[̲̅{}̲̅]", "░▒▓█ {} █▓▒░", "╔═══ {} ═══╗", "╚═══ {} ═══╝",
    "•┈••✦ {} ✦••┈•", "─── ⋆⋅☆⋅⋆ ── {} ── ⋆⋅☆⋅⋆ ──", "✩ ₊˚ {} ⊹♡", "♱ {} ♱", "⸸ {} ⸸"
]

EMOJIS = ["🌸", "🦋", "🍃", "🔥", "👑", "🎸", "⚜️", "✨", "🖤", "💎", "🌙", "☀️", "⚡", "🍷", "🕊️", "💀", "☠️", "👾", "🤖", "❤️", "💙", "💚", "💛", "🧡", "💜", "🤍", "🤎", "💔", "💕", "❣️", "🎵", "🎶", "🎧", "🎤", "🎼", "🎹", "🥁", "🎷", "🎺", "🎻"]

def generate_styles(name: str) -> list:
    styles = set()
    stylized_names = {f_name: func(name) for f_name, func in FONTS.items()}
    
    # 1. Pure Emoji + Font + Emoji
    for s_name in stylized_names.values():
        for emoji in EMOJIS:
            styles.add(f"{emoji} {s_name} {emoji}")
            
    # 2. Apply all frames to all fonts
    for s_name in stylized_names.values():
        for frame in FRAMES:
            styles.add(frame.format(s_name))

    # 3. Double Emoji + Frame
    for s_name in stylized_names.values():
        for i in range(0, len(FRAMES), 3):
            frame = FRAMES[i]
            emo1 = random.choice(EMOJIS)
            emo2 = random.choice(EMOJIS)
            styles.add(f"{emo1} {frame.format(s_name)} {emo2}")

    # 4. Special Strikethrough / Underline / Zalgo
    for s_name in stylized_names.values():
        styles.add("".join([c + "\u0336" for c in s_name]))
        styles.add("".join([c + "\u0332" for c in s_name]))
        
    # 5. Mix and Match until 600+ styles
    all_frames = FRAMES + [""]
    all_names = list(stylized_names.values())
    
    while len(styles) < 600:
        frame = random.choice(all_frames)
        nm = random.choice(all_names)
        emo1 = random.choice(EMOJIS + [""])
        emo2 = random.choice(EMOJIS + [""])
        sp = random.choice([" ", "  ", "", " "])
        
        base = frame.format(nm) if frame else nm
        styles.add(f"{emo1}{sp}{base}{sp}{emo2}".strip())

    style_list = list(styles)
    random.shuffle(style_list)
    return style_list

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
    
    items_per_page = 20
    total_pages = math.ceil(len(styles) / items_per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_styles = styles[start_idx:end_idx]
    
    # Premium Card Format
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
        return await cq.answer("🚫 Ye tumhare liye nahi hai! Khud /style command use karo.", show_alert=True)
        
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
