def format_duration(seconds: int) -> str:
    if not seconds: return "00:00"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def make_progress_bar(current: int, total: int, length: int = 7) -> str:
    if total <= 0: return "─" * length
    pos = int(length * current / total)
    pos = max(0, min(pos, length - 1))
    # Thin line with circle
    return "─" * pos + "○" + "─" * (length - pos - 1) if length > 1 else "○"
