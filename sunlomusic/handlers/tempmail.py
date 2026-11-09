# Copyright (C) @YO_UR_OFFICIAL_CRUSH
import re
import time
import random
import string
import hashlib
import requests
from bs4 import BeautifulSoup
from pyrogram.enums import ParseMode, ChatType
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sunlomusic.core.logging import logger

token_map = {}
user_tokens = {}
MAX_MESSAGE_LENGTH = 4000
BASE_URL = "https://api.mail.tm"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def short_id_generator(email):
    unique_string = email + str(time.time())
    return hashlib.md5(unique_string.encode()).hexdigest()[:10]

def generate_random_username(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def get_domain():
    try:
        response = requests.get(f"{BASE_URL}/domains", headers=HEADERS, timeout=10)
        data = response.json()
        if isinstance(data, list) and data:
            return data[0]['domain']
        elif 'hydra:member' in data and data['hydra:member']:
            return data['hydra:member'][0]['domain']
    except Exception as e:
        logger.error(f"TempMail get_domain error: {e}")
    return None

def create_account(email, password):
    try:
        data = {"address": email, "password": password}
        response = requests.post(f"{BASE_URL}/accounts", headers=HEADERS, json=data, timeout=10)
        if response.status_code in [200, 201]:
            return response.json()
    except Exception as e:
        logger.error(f"TempMail create_account error: {e}")
    return None

def get_token(email, password):
    try:
        data = {"address": email, "password": password}
        response = requests.post(f"{BASE_URL}/token", headers=HEADERS, json=data, timeout=10)
        if response.status_code == 200:
            return response.json().get('token')
    except Exception as e:
        logger.error(f"TempMail get_token error: {e}")
    return None

def get_text_from_html(html_content_list):
    try:
        html_content = ''.join(html_content_list)
        soup = BeautifulSoup(html_content, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            url = a_tag['href']
            new_content = f"{a_tag.text} [{url}]"
            a_tag.string = new_content
        text_content = soup.get_text()
        return re.sub(r'\s+', ' ', text_content).strip()
    except Exception:
        return "Could not parse email content."

def list_messages(token):
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=10)
        data = response.json()
        if isinstance(data, list):
            return data
        elif 'hydra:member' in data:
            return data['hydra:member']
    except Exception as e:
        logger.error(f"TempMail list_messages error: {e}")
    return []

def register_tempmail_handlers(app: Client):
    logger.info("Registering TempMail handlers...")

    @app.on_message(filters.command('tstart'))
    async def start_temp(client, message):
        await message.reply("**Welcome to SunloMusic Temp Mail!**\n\n"
                            "Commands:\n"
            "➢ `/tmail` - Generate a random mail.\n"
            "➢ `/cmail [mail token]` - Check mails.\n")

    @app.on_message(filters.command('tmail'))
    async def generate_mail(client, message):
        logger.info(f"User {message.from_user.id} requested /tmail")
        if message.chat.type != ChatType.PRIVATE:
            await message.reply("**Please use this bot in private chat for TempMail.**")
            return
        
        loading_msg = await message.reply("**Generating your temporary email...**")
        
        domain = get_domain()
        if not domain:
            await loading_msg.edit_text("**Failed to connect to TempMail API (Domain error). Try again later.**")
            return
        
        username = generate_random_username()
        password = generate_random_password()
        email = f"{username}@{domain}"
        
        account = create_account(email, password)
        if not account:
            await loading_msg.edit_text("**Failed to create account. Username might be taken.**")
            return
        
        token = get_token(email, password)
        if not token:
            await loading_msg.edit_text("**Failed to retrieve token.**")
            return
        
        short_id = short_id_generator(email)
        token_map[short_id] = token
        
        output = (f"**📧 SunloMusic Email Details**\n"
                  f"━━━━━━━━━━━━━━━━━━\n"
                  f"**Email:** `{email}`\n"
                  f"**Password:** `{password}`\n"
                  f"**Token:** `{token}`\n"
                  f"━━━━━━━━━━━━━━━━━━\n"
                  f"**Note:** Save the token to check mails using `/cmail`")
        
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Check Emails", callback_data=f"check_{short_id}")]])
        await loading_msg.edit_text(output, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(r'^check_'))
    async def check_mail(client, callback_query):
        short_id = callback_query.data.split('_')[1]
        token = token_map.get(short_id)
        
        if not token:
            await callback_query.answer("Session expired. Use /cmail with your token.", show_alert=True)
            return
        
        user_tokens[callback_query.from_user.id] = token
        messages = list_messages(token)
        
        if not messages:
            await callback_query.answer("Inbox is empty ❌", show_alert=True)
            return
        
        output = "**📬 Your Messages:**\n\n"
        buttons = []
        for idx, msg in enumerate(messages[:10], 1):
            output += f"{idx}. From: `{msg['from']['address']}`\nSubject: {msg['subject']}\n\n"
            buttons.append(InlineKeyboardButton(f"{idx}", callback_data=f"read_{msg['id']}"))
        
        keyboard = [buttons[i:i+5] for i in range(0, len(buttons), 5)]
        await callback_query.message.reply(output, reply_markup=InlineKeyboardMarkup(keyboard))

    @app.on_callback_query(filters.regex(r"^close_message"))
    async def close_message(client, callback_query):
        await callback_query.message.delete()

    @app.on_callback_query(filters.regex(r"^read_"))
    async def read_message(client, callback_query):
        message_id = callback_query.data.split('_')[1]
        token = user_tokens.get(callback_query.from_user.id)
        
        if not token:
            await callback_query.message.reply("**Token not found. Please use /cmail again.**")
            return
        
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages/{message_id}", headers=headers)
        
        if response.status_code == 200:
            details = response.json()
            message_text = get_text_from_html(details.get('html', [])) if 'html' in details else details.get('text', 'Content not available.')
            
            if len(message_text) > MAX_MESSAGE_LENGTH:
                message_text = message_text[:MAX_MESSAGE_LENGTH - 100] + "... [truncated]"
            
            output = f"**From:** `{details['from']['address']}`\n**Subject:** `{details['subject']}`\n━━━━━━━━━━━━━━━━━━\n{message_text}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_message")]])
            await callback_query.message.reply(output, disable_web_page_preview=True, reply_markup=keyboard)
        else:
            await callback_query.message.reply("**Error retrieving message.**")

    @app.on_message(filters.command('cmail'))
    async def manual_check_mail(client, message):
        if message.chat.type != ChatType.PRIVATE:
            await message.reply("**Please use this in private chat.**")
            return
        
        token = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        if not token:
            await message.reply("**Usage:** `/cmail [token]`")
            return
        
        loading_msg = await message.reply("**⏳ Checking...**")
        user_tokens[message.from_user.id] = token
        messages = list_messages(token)
        
        if not messages:
            await loading_msg.edit_text("**❌ Inbox is empty or invalid token.**")
            return
        
        output = "**📬 Your Messages:**\n\n"
        buttons = []
        for idx, msg in enumerate(messages[:10], 1):
            output += f"{idx}. From: `{msg['from']['address']}`\nSubject: {msg['subject']}\n\n"
            buttons.append(InlineKeyboardButton(f"{idx}", callback_data=f"read_{msg['id']}"))
        
        keyboard = [buttons[i:i+5] for i in range(0, len(buttons), 5)]
        await loading_msg.edit_text(output, reply_markup=InlineKeyboardMarkup(keyboard))
