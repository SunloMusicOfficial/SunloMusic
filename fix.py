import os, re
OLD_BOT = "SunloMusic"
NEW_BOT = "SunloMusic"
OLD_USER = "SunloMusicOfficial"
NEW_USER = "SunloMusicOfficial"

for root, dirs, files in os.walk("."):
    if ".git" in root: continue
    for file in files:
        if file.endswith(('.py', '.md', '.env', '.txt', '.yml', '.json')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                text = re.sub(OLD_BOT, NEW_BOT, text, flags=re.IGNORECASE)
                text = re.sub(OLD_USER, NEW_USER, text, flags=re.IGNORECASE)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
            except: pass
print("✅ Sab kuch SunloMusic mein convert ho gaya!")
