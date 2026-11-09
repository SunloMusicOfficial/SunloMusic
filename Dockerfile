# Use official Python 3.11 slim image (Best for Pyrogram/PyTgCalls)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Kolkata

# Install system dependencies (FFmpeg for VC, Node & Deno for yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    npm \
    curl \
    unzip \
    git \
    build-essential \
    && curl -fsSL https://deno.land/install.sh | sh \
    && mv /root/.deno/bin/deno /usr/local/bin/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's code
COPY . .

# Create necessary directories for the bot
RUN mkdir -p downloads cookies logs assets

# Expose the port for Render's keep-alive web server
EXPOSE 8080

# Start the bot
CMD ["python", "bot.py"]
