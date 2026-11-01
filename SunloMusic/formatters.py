def format_duration(seconds: int) -> str:
    if not seconds: return "00:00"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    # ✅ Hata diya leading zero minutes me (e.g. 1:45 instead of 01:45)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def make_progress_bar(current: int, total: int, length: int = 8) -> str:
    """Generates the premium thick bar with hollow boxes and a music note."""
    if total <= 0: return "━" * length
    pos = int(length * current / total)
    pos = max(0, min(pos, length - 1))
    
    # ✅ Exact style: Thick solid lines, Music Note, Hollow rectangles
    return "━" * pos + "🎵" + "▭" * (length - pos)
