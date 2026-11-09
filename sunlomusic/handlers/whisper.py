import html
import uuid
import os
from pyrogram import Client, filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ButtonStyle, ParseMode
from sunlomusic.core.logging import logger
from sunlomusic.db import db

# Collections
messages_col = db["whisper_messages"]

def register_whisper_handlers(app: Client):
    @app.on_inline_query()
    async def whisper_inline(client, inline_query):
        text = inline_query.query.strip()
        sender_id = inline_query.from_user.id

        if not text:
            await inline_query.answer(
                results=[InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="How to Send Secret Message",
                    description="Include recipient's @username or user ID at the end.",
                    input_message_content=InputTextMessageContent(
                        "How to Send Secret Message\n\n"
                        "Include the recipient's @username or user ID at the end.\n\n"
                        "Example: @SunloMusicBot Hello there! @username"
                    )
                )],
                cache_time=1
            )
            return

        parts = text.split()
        recipient_identifier = parts[-1]

        if not (recipient_identifier.startswith("@") or recipient_identifier.isdigit()):
            return

        message_content = " ".join(parts[:-1])
        if not message_content:
            return

        message_id = str(uuid.uuid4())
        recipient_id = None
        full_name = "the recipient"

        if recipient_identifier.startswith("@"):
            recipient_username = recipient_identifier[1:]
            try:
                user = await client.get_users(recipient_username)
                recipient_id = user.id
                full_name = user.first_name
            except Exception:
                await inline_query.answer(results=[InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Recipient Not Found",
                    description="User not found or hasn't started the bot.",
                    input_message_content=InputTextMessageContent(
                        "Recipient not found. Ask them to start the bot first."
                    )
                )])
                return
        elif recipient_identifier.isdigit():
            recipient_id = int(recipient_identifier)
            try:
                user = await client.get_users(recipient_id)
                full_name = user.first_name
            except Exception:
                await inline_query.answer(results=[InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Ask Recipient to Start the Bot",
                    description="Recipient hasn't started the bot yet.",
                    input_message_content=InputTextMessageContent(
                        "Please ask the recipient to start the bot first."
                    )
                )])
                return

        await messages_col.insert_one({
            "_id": message_id,
            "content": message_content,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "recipient_name": full_name,
            "read": False
        })

        safe_name = html.escape(full_name)
        mention_link = f'<a href="tg://user?id={recipient_id}">{safe_name}</a>'
        whisper_text = f"🔒 Whisper to {mention_link}, only viewable by you and them."

        results = [InlineQueryResultArticle(
            id=message_id,
            title=f"A whisper message to {full_name}",
            description=f"Only {full_name} can open this whisper.",
            input_message_content=InputTextMessageContent(
                whisper_text, parse_mode=ParseMode.HTML
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(" Open Whisper", callback_data=message_id)
            ]])
        )]

        await inline_query.answer(results, cache_time=1)

    @app.on_callback_query(filters.regex(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"))
    async def whisper_callback(client, callback_query):
        message_id = callback_query.data
        user_id = callback_query.from_user.id

        message_data = await messages_col.find_one({"_id": message_id})
        if not message_data:
            await callback_query.answer("Message not found or expired.", show_alert=True)
            return

        sender_id = message_data["sender_id"]
        recipient_id = message_data["recipient_id"]

        if user_id == sender_id or user_id == recipient_id:
            content = message_data["content"]
            await callback_query.answer(f"{content}", show_alert=True)

            if user_id == recipient_id and not message_data.get("read"):
                await messages_col.update_one({"_id": message_id}, {"$set": {"read": True}})
                updated_text = f"🔒 Whisper to {message_data.get('recipient_name')} (Read ✅)"
                updated_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(" Open Whisper", callback_data=message_id, style=ButtonStyle.SUCCESS)
                ]])
                try:
                    await callback_query.edit_message_text(
                        text=updated_text, reply_markup=updated_markup, parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
        else:
            await callback_query.answer("Hey Dear! This Message is Not For You", show_alert=True)
