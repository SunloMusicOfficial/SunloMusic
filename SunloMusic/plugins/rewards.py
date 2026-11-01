from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    claim_daily, get_daily_cooldown, add_coins, get_coins,
    spend_coins, add_purchase, get_purchases, is_sudo
)

DAILY_AMOUNT = 50

SHOP_ITEMS = {
    "vip":     {"name": "👑 VIP Tag",        "price": 500,  "desc": "Exclusive VIP badge in leaderboard"},
    "skip5":   {"name": "⏭ 5x Skip Power",   "price": 100,  "desc": "Skip any song without admin (5 times)"},
    "custom":  {"name": "🎨 Custom Thumb",    "price": 200,  "desc": "Set custom thumbnail for group (DM bot)"},
    "download": {"name": "📥 10x Free Download", "price": 300, "desc": "10 free /song downloads"},
}

@bot.on_message(filters.command("daily"))
@catch_errors
async def daily_cmd(_, m: Message):
    user_id = m.from_user.id
    if await is_sudo(user_id):
        return await m.reply_text("👑 <b>You are the Owner/Sudo.</b>\nYou already have unlimited coins, no need for daily rewards!")
        
    result = await claim_daily(user_id)
    
    if result is None:
        remaining = await get_daily_cooldown(user_id)
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        return await m.reply_text(
            f"⏳ <b>Already claimed today!</b>\n\n"
            f"Come back in <code>{hrs}h {mins}m</code>"
        )
    
    new_balance = await add_coins(user_id, DAILY_AMOUNT)
    await m.reply_text(
        f"🎁 <b>Daily Reward Claimed!</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"💰 <b>+{DAILY_AMOUNT} coins</b>\n"
        f"💵 <b>Balance:</b> <code>{new_balance}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"<i>Come back tomorrow for more!</i>"
    )

@bot.on_message(filters.command("points"))
@catch_errors
async def points_cmd(_, m: Message):
    user_id = m.from_user.id
    is_priv = await is_sudo(user_id)
    bal = "∞ (Unlimited)" if is_priv else await get_coins(user_id)
    
    await m.reply_text(
        f"💰 <b>Your Balance</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👤 User: {m.from_user.mention}\n"
        f"💵 Coins: <code>{bal}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"💡 Claim daily: /daily\n"
        f"🛒 Shop: /shop\n"
        f"🎁 Gift: Reply to user with /gift amount"
    )

@bot.on_message(filters.command("shop"))
@catch_errors
async def shop_cmd(_, m: Message):
    user_id = m.from_user.id
    is_priv = await is_sudo(user_id)
    bal = "∞" if is_priv else await get_coins(user_id)
    
    text = f"🛒 <b>Coins Shop</b>\n━━━━━━━━━━━━━\n💵 Your balance: <code>{bal}</code>\n━━━━━━━━━━━━━\n\n"
    
    buttons = []
    for key, item in SHOP_ITEMS.items():
        text += f"{item['name']} — <code>{item['price']}💰</code>\n<i>{item['desc']}</i>\n\n"
        buttons.append([InlineKeyboardButton(
            f"{item['name']} ({item['price']}💰)",
            callback_data=f"buy_{key}"
        )])
    
    await m.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("^buy_"))
@catch_errors
async def buy_cb(_, cq: CallbackQuery):
    key = cq.data.replace("buy_", "")
    if key not in SHOP_ITEMS:
        return await cq.answer("Invalid item", show_alert=True)
    
    item = SHOP_ITEMS[key]
    user_id = cq.from_user.id
    is_priv = await is_sudo(user_id)
    
    purchased = await get_purchases(user_id)
    if key in purchased and key != "skip5":
        return await cq.answer(f"You already own {item['name']}!", show_alert=True)
    
    if not is_priv:
        bal = await get_coins(user_id)
        if bal < item["price"]:
            return await cq.answer(
                f"❌ Not enough coins!\nNeed: {item['price']}\nHave: {bal}",
                show_alert=True
            )
        
        success = await spend_coins(user_id, item["price"])
        if not success:
            return await cq.answer("❌ Purchase failed!", show_alert=True)
    
    await add_purchase(user_id, key)
    await cq.answer(f"✅ Purchased {item['name']}!", show_alert=True)
    try: await cq.message.delete()
    except: pass
    await bot.send_message(user_id, f"🎉 <b>Purchase Successful!</b>\n\n{item['name']}\n<i>{item['desc']}</i>\n\n" + ("<i>(Owner bypass: 0 coins deducted)</i>" if is_priv else ""))

# ✅ NEW: GIFT / PAY COMMAND
@bot.on_message(filters.command(["gift", "pay"]))
@catch_errors
async def gift_cmd(_, m: Message):
    user_id = m.from_user.id
    is_priv = await is_sudo(user_id)
    
    target_id = None
    amount = 0
    
    if m.reply_to_message:
        target_id = m.reply_to_message.from_user.id
        if len(m.command) < 2:
            return await m.reply_text("❌ <b>Usage:</b> Reply to user with <code>/gift amount</code>")
        try:
            amount = int(m.command[1])
        except:
            return await m.reply_text("❌ <b>Invalid amount.</b>")
    else:
        if len(m.command) < 3:
            return await m.reply_text("❌ <b>Usage:</b> <code>/gift user_id amount</code>\nOr reply to a user with <code>/gift amount</code>")
        try:
            target_id = int(m.command[1])
            amount = int(m.command[2])
        except:
            return await m.reply_text("❌ <b>Invalid ID or amount.</b>")

    if amount <= 0:
        return await m.reply_text("❌ Amount must be greater than 0.")
    if target_id == user_id:
        return await m.reply_text("❌ You cannot gift yourself.")

    if not is_priv:
        # Normal users must have enough balance
        if not await spend_coins(user_id, amount):
            return await m.reply_text("❌ <b>You don't have enough coins!</b>")
    
    # Add to target
    new_bal = await add_coins(target_id, amount)
    
    gift_msg = (
        f"🎁 <b>Coins Transferred!</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👤 <b>From:</b> {m.from_user.mention}\n"
        f"🎯 <b>To:</b> <a href='tg://user?id={target_id}'>User</a>\n"
        f"💰 <b>Amount:</b> <code>{amount}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"💵 <b>Receiver's New Balance:</b> <code>{new_bal}</code>\n"
    )
    if is_priv:
        gift_msg += "\n<i>(Owner bypass: 0 coins deducted from you)</i>"
        
    await m.reply_text(gift_msg)
