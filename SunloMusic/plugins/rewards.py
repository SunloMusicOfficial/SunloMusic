from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    claim_daily, get_daily_cooldown, add_coins, get_coins,
    spend_coins, add_purchase, get_purchases
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
    bal = await get_coins(m.from_user.id)
    await m.reply_text(
        f"💰 <b>Your Balance</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👤 User: {m.from_user.mention}\n"
        f"💵 Coins: <code>{bal}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"💡 Claim daily: /daily\n"
        f"🛒 Shop: /shop"
    )

@bot.on_message(filters.command("shop"))
@catch_errors
async def shop_cmd(_, m: Message):
    bal = await get_coins(m.from_user.id)
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
    
    purchased = await get_purchases(user_id)
    if key in purchased and key != "skip5":
        return await cq.answer(f"You already own {item['name']}!", show_alert=True)
    
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
    await bot.send_message(user_id, f"🎉 <b>Purchase Successful!</b>\n\n{item['name']}\n<i>{item['desc']}</i>")
