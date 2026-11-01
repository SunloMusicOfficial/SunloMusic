def format_duration(seconds: int) -> str:
    if not seconds: return "00:00"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def make_progress_bar(current: int, total: int, length: int = 8) -> str:
    """Generates thick solid blocks for progress and hollow blocks for remaining."""
    if total <= 0: return "▬" * length
    pos = int(length * current / total)
    pos = max(0, min(pos, length - 1))
    
    # ✅ Thick solid blocks (▬) for filled, Music Note (🎵), Hollow blocks (▭) for empty
    return "▬" * pos + "🎵" + "▭" * (length - pos)
