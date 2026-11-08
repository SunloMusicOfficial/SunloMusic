import os

# 1. Config mein API KEY add karein
config_file = "sunlomusic/core/config.py"
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        lines = f.readlines()
    
    api_line = '    SUNLOMUSIC_API_KEY = os.getenv("SUNLOMUSIC_API_KEY", "")\n'
    if not any("SUNLOMUSIC_API_KEY" in line for line in lines):
        for i, line in enumerate(lines):
            if "class Config:" in line:
                lines.insert(i+1, api_line)
                break
        with open(config_file, "w") as f:
            f.writelines(lines)

# 2. Downloader file ko update karein
downloader_file = "sunlomusic/services/downloader.py"
if os.path.exists(downloader_file):
    print("✅ Found downloader.py. Please check the download function to integrate sunlomusic_api.")

print("✅ SunloMusic API Module ready!")
print("⚠️ IMPORTANT: Please replace your yt-dlp logic inside downloader.py with this:")
print("from sunlomusic.services.sunlomusic_api import download_with_sunlomusic_api")
