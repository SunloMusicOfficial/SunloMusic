import os
import re

print("🔍 Scanning repo for YouTube logic...")

# Check folder name (Telecast ya sunlomusic)
base_dir = "sunlomusic"
if os.path.exists("Telecast"):
    base_dir = "Telecast"

# 1. Create the API file
api_code = """import os
import requests

def download_with_sunlomusic_api(video_id, media_type="audio"):
    api_key = os.getenv("SUNLOMUSIC_API_KEY")
    if not api_key:
        print("❌ SUNLOMUSIC_API_KEY missing in environment.")
        return None
        
    api_url = "https://api.shrutibots.in/download"
    os.makedirs("downloads", exist_ok=True)
    
    ext = "mp3" if media_type == "audio" else "mp4"
    file_path = f"downloads/{video_id}.{ext}"
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    params = {"url": video_id, "type": media_type, "api_key": api_key}

    try:
        print(f"⬇️ Downloading via SunloMusic API: {video_id}")
        response = requests.get(api_url, params=params, stream=True, timeout=300)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=131072):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Download Complete: {file_path}")
            return file_path
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request Failed: {e}")
        return None
"""

api_path = os.path.join(base_dir, "services", "sunlomusic_api.py")
with open(api_path, "w") as f:
    f.write(api_code)

# 2. Patch downloader.py and yt_search.py
files_to_patch = [
    os.path.join(base_dir, "services", "downloader.py"),
    os.path.join(base_dir, "services", "yt_search.py")
]

for file_path in files_to_patch:
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {file_path}.bak")
        
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        code = code.replace("Shruti", "SunloMusic")
        
        if "from sunlomusic.services.sunlomusic_api import download_with_sunlomusic_api" not in code:
            code = "from sunlomusic.services.sunlomusic_api import download_with_sunlomusic_api\n" + code

        if "downloader.py" in file_path:
            code = re.sub(r"cmd\s*=\s*\[.*?yt-dlp.*?\]", "file_path = download_with_sunlomusic_api(url, media_type)", code, flags=re.DOTALL)
            code = re.sub(r"with yt_dlp\.YoutubeDL.*?as ydl:.*?ydl\.download\(.*?\)", "file_path = download_with_sunlomusic_api(url, media_type)", code, flags=re.DOTALL)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"✅ Patched: {file_path}")

print("🎉 All done! SunloMusic API is now integrated.")
