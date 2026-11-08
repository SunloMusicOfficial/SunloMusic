import os
import requests

def download_with_sunlomusic_api(video_id, media_type="audio"):
    api_key = os.getenv("SUNLOMUSIC_API_KEY")
    if not api_key:
        print("❌ SUNLOMUSIC_API_KEY missing in environment.")
        return None
        
    # API Base URL
    api_url = "https://api.shrutibots.in/download"
    
    os.makedirs("downloads", exist_ok=True)
    
    ext = "mp3" if media_type == "audio" else "mp4"
    file_path = f"downloads/{video_id}.{ext}"
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    params = {
        "url": video_id,
        "type": media_type,
        "api_key": api_key
    }

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
