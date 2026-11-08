import os

BAD_WORDS = ["SunloMusicOfficial", "SunloMusicOfficial", "SunloMusicOfficial", "SunloMusicOfficial", "SunloMusicOfficial", "SunloMusicOfficial"]

for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root: continue
    for file in files:
        if file.endswith(('.py', '.md', '.env', '.txt', '.yml', '.json', '.sh')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                for word in BAD_WORDS:
                    text = text.replace(word, "SunloMusicOfficial") # Ya kuch bhi khali chhod dein
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
            except: pass
print("✅ Pura code scan aur clean ho gaya!")
