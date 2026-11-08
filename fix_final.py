import os, re

# Purane aur naye naam
OLD_FOLDER = "sunlomusic"
NEW_FOLDER = "sunlomusic"

OLD_DEV = "YO_UR_OFFICIAL_CRUSH"
NEW_DEV = "YO_UR_OFFICIAL_CRUSH"

OLD_GROUP = "Vip_Sakil_Bio"
NEW_GROUP = "Vip_Sakil_Bio"

# 1. Text replacement inside files
for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root: continue
    for file in files:
        if file.endswith(('.py', '.md', '.env', '.txt', '.yml', '.json', '.sh')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Replaces
                text = text.replace("SunloMusic", "SunloMusic")
                text = text.replace("sunlomusic", "sunlomusic")
                text = text.replace(OLD_DEV, NEW_DEV)
                text = text.replace(OLD_GROUP, NEW_GROUP)
                text = text.replace("SunloMusicOfficial", "SunloMusicOfficial")
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
            except: pass

# 2. Folder ka naam badalna
if os.path.exists(OLD_FOLDER):
    os.rename(OLD_FOLDER, NEW_FOLDER)
    
print("✅ Folder rename aur Text replacement done!")
