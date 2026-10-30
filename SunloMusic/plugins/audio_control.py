import time
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import get_queue
from SunloMusic.calls import play_stream, AUDIO_CONTROLS

@bot.on_message(filters.command("speed") & filters.group)
@catch_errors
@admin_only
async def speed_cmd(_, m: Message):
    if len(m.command) < 2:
        ctrl = AUDIO_CONTROLS.get(m.chat.id, {})
        current = ctrl.get("speed", 1.0)
        return await m.reply_text(
            f"⚡ <b>Current Speed:</b> <code>{current}x</code>\n\n"
            f"<b>Usage:</b> <code>/speed 1.25</code>\n\n"
            f"<b>Options:</b> 0.5, 0.75, 1.0, 1.25, 1.5, 2.0"
        )
    
    try: speed = float(m.command[1])
    except: return await m.reply_text("❌ <b>Invalid number.</b> Use 0.5 to 2.0")
    
    if speed < 0.5 or speed > 2.0:
        return await m.reply_text("❌ <b>Speed must be between 0.5 and 2.0</b>")
    
    q = get_queue(m.chat.id)
    if not q.now_playing:
        return await m.reply_text("❌ <b>Nothing is playing.</b>")
    
    if m.chat.id not in AUDIO_CONTROLS:
        AUDIO_CONTROLS[m.chat.id] = {}
    AUDIO_CONTROLS[m.chat.id]["speed"] = speed
    
    status = await m.reply_text(f"⚡ <b>Speed set to {speed}x</b>\nRestarting song...")
    
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video)
    q.start_time = time.time(); q.total_paused = 0; q.paused = False
    
    await status.edit_text(f"✅ <b>Speed: {speed}x</b> — Applied!")

@bot.on_message(filters.command("volume") & filters.group)
@catch_errors
@admin_only
async def volume_cmd(_, m: Message):
    if len(m.command) < 2:
        ctrl = AUDIO_CONTROLS.get(m.chat.id, {})
        current = int(ctrl.get("volume", 1.0) * 100)
        return await m.reply_text(
            f"🔊 <b>Current Volume:</b> <code>{current}%</code>\n\n"
            f"<b>Usage:</b> <code>/volume 150</code> (0-200)"
        )
    
    try: vol = int(m.command[1])
    except: return await m.reply_text("❌ <b>Invalid number.</b>")
    
    if vol < 0 or vol > 200:
        return await m.reply_text("❌ <b>Volume must be 0-200</b>")
    
    q = get_queue(m.chat.id)
    if not q.now_playing:
        return await m.reply_text("❌ <b>Nothing is playing.</b>")
    
    if m.chat.id not in AUDIO_CONTROLS:
        AUDIO_CONTROLS[m.chat.id] = {}
    AUDIO_CONTROLS[m.chat.id]["volume"] = vol / 100.0
    
    status = await m.reply_text(f"🔊 <b>Volume set to {vol}%</b>\nRestarting...")
    
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video)
    q.start_time = time.time(); q.total_paused = 0; q.paused = False
    
    await status.edit_text(f"✅ <b>Volume: {vol}%</b> — Applied!")

@bot.on_message(filters.command("eq") & filters.group)
@catch_errors
@admin_only
async def eq_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text(
            "<b>🎛 Equalizer Presets</b>\n\n"
            "<b>Usage:</b> <code>/eq rock</code>\n\n"
            "<b>Options:</b> bass, pop, rock, jazz, vocal, flat"
        )
    
    eq = m.command[1].lower()
    valid = ["bass", "pop", "rock", "jazz", "vocal", "flat"]
    if eq not in valid:
        return await m.reply_text(f"❌ <b>Invalid EQ.</b> Choose: {', '.join(valid)}")
    
    q = get_queue(m.chat.id)
    if not q.now_playing:
        return await m.reply_text("❌ <b>Nothing is playing.</b>")
    
    if m.chat.id not in AUDIO_CONTROLS:
        AUDIO_CONTROLS[m.chat.id] = {}
    AUDIO_CONTROLS[m.chat.id]["eq"] = "none" if eq == "flat" else eq
    
    status = await m.reply_text(f"🎛 <b>EQ: {eq}</b>\nRestarting...")
    
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video)
    q.start_time = time.time(); q.total_paused = 0; q.paused = False
    
    await status.edit_text(f"✅ <b>EQ: {eq.upper()}</b> — Applied!")
