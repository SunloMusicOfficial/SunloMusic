import os
import asyncio
import io
import PIL.Image
from google import genai
from pyrogram import Client, filters
from pyrogram.types import Message
from sunlomusic.core.logging import logger

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def register_gemini_handlers(app: Client):
    @app.on_message(filters.command("gem"))
    async def gemini_handler(client_app: Client, message: Message):
        if not client:
            await message.reply_text("❌ **Gemini API Key is not configured.**")
            return
        
        if len(message.text.strip()) <= 5:
            await message.reply_text("**Provide a prompt after the command.**")
            return
            
        loading_message = await message.reply_text("**Generating response, please wait...**")
        prompt = message.text.split(maxsplit=1)[1]
        
        try:
            # Use new google-genai SDK
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=prompt
            )
            response_text = response.text
            
            if len(response_text) > 4000:
                parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
                for part in parts:
                    await message.reply_text(part)
            else:
                await message.reply_text(response_text)
        except Exception as e:
            await message.reply_text(f"**An error occurred: {str(e)}**")
        finally:
            await loading_message.delete()

    @app.on_message(filters.command("imgai"))
    async def image_ai_handler(client_app: Client, message: Message):
        if not client:
            await message.reply_text("❌ **Gemini API Key is not configured.**")
            return
            
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("**Please reply to a photo for a response.**")
            return
        
        prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."
        processing_message = await message.reply_text("**Generating response, please wait...**")
        
        try:
            img_data = await client_app.download_media(message.reply_to_message, in_memory=True)
            img = PIL.Image.open(io.BytesIO(img_data.getbuffer()))
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=[prompt, img]
            )
            await message.reply_text(response.text, parse_mode=None)
        except Exception as e:
            logger.error(f"Error during image analysis: {e}")
            await message.reply_text("**An error occurred. Please try again.**")
        finally:
            await processing_message.delete()
