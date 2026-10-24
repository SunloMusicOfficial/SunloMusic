FROM python:3.12-slim-bookworm

WORKDIR /app

# Install required system packages and heavy compilers for Python 3.12
RUN apt-get update -y && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
