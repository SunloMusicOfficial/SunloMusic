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

user_data = {}
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
    response = requests.get(f"{BASE_URL}/domains", headers=HEADERS)
    data = response.json()
    if isinstance(data, list) and data:
        return data[0]['domain']
    elif 'hydra:member' in data and data['hydra:member']:
        return data['hydra:member'][0]['domain']
    return None

def create_account(email, password):
    data = {"address": email, "password": password}
    response = requests.post(f"{BASE_URL}/accounts", headers=HEADERS, json=data)
    if response.status_code in [200, 201]:
        return response.json()
    return None

def get_token(email, password):
    data = {"address": email, "password": password}
    response = requests.post(f"{BASE_URL}/token", headers=HEADERS, json=data)
    if response.status_code == 200:
        return response.json().get('token')
    return None

def get_text_from_html(html_content_list):
    html_content = ''.join(html_content_list)
    soup = BeautifulSoup(html_content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        url = a_tag['href']
        new_content = f"{a_tag.text} [{url}]"
        a_tag.string = new_content
    text_content = soup.get_text()
    cleaned_content = re.sub(r'\s+', ' ', text_content).strip()
    return cleaned_content

def list_messages(token):
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    data = response.json()
    if isinstance(data, list):
        return data
    elif 'hydra:member' in data:
        return data['hydra:member']
    return []

def register_tempmail_handlers(app: Client):
    # Note: /start ko /tstart kar diya gaya hai taaki music bot se conflict na ho
    @app.on_message(filters.command('tstart'))
    async def start_temp(client, message):
        welcome_message = (
            "**Welcome to SunloMusic Temp Mail!** \n\n"
            "You can use the following commands to manage temporary email addresses:\n\n"
            "➢ `/tmail` - Generate a random mail with a password.\n"
            "➢ `/tmail [username]:[pass]` - Generate a specific mail with a password.\n"
            "➢ `/cmail [mail token]` - Check the 10 most recent mails using your mail token.\n\n"
            "✨ **Note:** When you generate a mail and password, you will receive a mail token. "
            "This token allows you to check the 10 most recent emails received by your temporary mail address. "
            "Each email has a different token, so please keep your tokens private and secure. ️"
        )
        await message.reply(welcome_message)

    @app.on_message(filters.command('tmail'))
    async def generate_mail(client, message):
        if message.chat.type != ChatType.PRIVATE:
            await message.reply("**Please use this bot in private chat only.**")
            return
        
        loading_msg = await message.reply("**Generating your temporary email...**")
        
        args_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        args = args_text.split()
        
        if len(args) == 1 and ':' in args[0]:
            username, password = args[0].split(':')
        else:
            username = generate_random_username()
            password = generate_random_password()
        
        domain = get_domain()
        if not domain:
            await message.reply("**Failed to retrieve domain try Again**")
            await client.delete_messages(message.chat.id, [loading_msg.message_id])
            return
        
        email = f"{username}@{domain}"
        account = create_account(email, password)
        if not account:
            await message.reply("**Username already taken. Choose another one.**")
            await client.delete_messages(message.chat.id, [loading_msg.message_id])
            return
        
        time.sleep(2)
        token = get_token(email, password)
        if not token:
            await message.reply("**Failed to retrieve token.**")
            await client.delete_messages(message.chat.id, [loading_msg.message_id])
            return
        
        short_id = short_id_generator(email)
        token_map[short_id] = token
        
        output_message = (
            "** SunloMusic Email Details **\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"** Email:** `{email}`\n"
            f"** Password:** `{password}`\n"
            f"** Token:** `{token}`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "**Note: Keep the token to Access Mail**"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Check Emails", callback_data=f"check_{short_id}")]])
        
        await message.reply(output_message, reply_markup=keyboard)
        await client.delete_messages(message.chat.id, [loading_msg.id])

    @app.on_callback_query(filters.regex(r'^check_'))
    async def check_mail(client, callback_query):
        short_id = callback_query.data.split('_')[1]
        token = token_map.get(short_id)
        
        if not token:
            await callback_query.message.reply("**Session expired, Please use /cmail with your token.**")
            return
        
        user_tokens[callback_query.from_user.id] = token
        messages = list_messages(token)
        
        if not messages:
            await callback_query.answer("No messages received ❌", show_alert=True)
            return
        
        loading_msg = await callback_query.message.reply("**⏳ Checking Mails.. Please wait.**")
        output = "** Your SunloMusic Messages **\n"
        output += "**━━━━━━━━━━━━━━━━━━**\n"
        buttons = []
        
        for idx, msg in enumerate(messages[:10], 1):
            output += f"{idx}. From: `{msg['from']['address']}` - Subject: {msg['subject']}\n"
            button = InlineKeyboardButton(f"{idx}", callback_data=f"read_{msg['id']}")
            buttons.append(button)
        
        keyboard = []
        for i in range(0, len(buttons), 5):
            keyboard.append(buttons[i:i+5])
        
        await callback_query.message.reply(output, reply_markup=InlineKeyboardMarkup(keyboard))
        await client.delete_messages(callback_query.message.chat.id, [loading_msg.id])

    @app.on_callback_query(filters.regex(r"^close_message"))
    async def close_message(client, callback_query):
        await callback_query.message.delete()

    @app.on_callback_query(filters.regex(r"^read_"))
    async def read_message(client, callback_query):
        message_id = callback_query.data.split('_')[1]
        token = user_tokens.get(callback_query.from_user.id)
        
        if not token:
            await callback_query.message.reply("**Token not found. Please use /cmail with your token again.**")
            return
        
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages/{message_id}", headers=headers)
        
        if response.status_code == 200:
            details = response.json()
            if 'html' in details:
                message_text = get_text_from_html(details['html'])
            elif 'text' in details:
                message_text = details['text']
            else:
                message_text = "Content not available."
            
            if len(message_text) > MAX_MESSAGE_LENGTH:
                message_text = message_text[:MAX_MESSAGE_LENGTH - 100] + "... [message truncated]"
            
            output = f"**From:** `{details['from']['address']}`\n**Subject:** `{details['subject']}`\n━━━━━━━━━━━━━━━━━━\n{message_text}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_message")]])
            
            await callback_query.message.reply(output, disable_web_page_preview=True, reply_markup=keyboard)
        else:
            await callback_query.message.reply("**Error retrieving message details.**")

    @app.on_message(filters.command('cmail'))
    async def manual_check_mail(client, message):
        if message.chat.type != ChatType.PRIVATE:
            await message.reply("**Please use this bot in private chat only.**")
            return
        
        loading_msg = await message.reply("**⏳ Checking Mails.. Please wait.**")
        token = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        
        if not token:
            await message.reply("**Please provide a token after the /cmail command.**")
            await client.delete_messages(message.chat.id, [loading_msg.id])
            return
        
        user_tokens[message.from_user.id] = token
        messages = list_messages(token)
        
        if not messages:
            await message.reply("**❌ No messages found or maybe wrong token**")
            await client.delete_messages(message.chat.id, [loading_msg.id])
            return
        
        output = "** Your SunloMusic Messages **\n"
        output += "**━━━━━━━━━━━━━━━━━━**\n"
        buttons = []
        
        for idx, msg in enumerate(messages[:10], 1):
            output += f"{idx}. From: {msg['from']['address']} - Subject: {msg['subject']}\n"
            button = InlineKeyboardButton(f"{idx}", callback_data=f"read_{msg['id']}")
            buttons.append(button)
        
        keyboard = []
        for i in range(0, len(buttons), 5):
            keyboard.append(buttons[i:i+5])
        
        await message.reply(output, reply_markup=InlineKeyboardMarkup(keyboard))
        await client.delete_messages(message.chat.id, [loading_msg.id])
