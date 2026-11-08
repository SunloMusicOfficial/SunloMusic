import os

# Purana aur naya naam
OLD_BOT = "SunloMusicBot"
NEW_BOT = "SunloMusicBot"

for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root: continue
    for file in files:
        if file.endswith(('.py', '.md', '.env', '.txt', '.yml', '.json', '.sh')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Replace with and without @
                text = text.replace("@" + OLD_BOT, "@" + NEW_BOT)
                text = text.replace(OLD_BOT, NEW_BOT)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
            except: pass

print("✅ SunloMusicBot ko @SunloMusicBot se replace kar diya gaya!")
