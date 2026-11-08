# Copyright (C) @YO_UR_OFFICIAL_CRUSH

AUDIO_EFFECTS = {
    "none": "",
    "bassboost": "aformat=sample_fmts=fltp,bass=g=10:f=110:w=0.6,alimiter=limit=0.9:level=disabled",
    "nightcore": "aresample=48000,asetrate=48000*1.25,aresample=48000",
    "slowed": "aresample=48000,asetrate=48000*0.85,aresample=48000",
    "lofi": "aresample=48000,asetrate=48000*0.9,aresample=48000,lowpass=f=3000",
    "8d": "aformat=channel_layouts=stereo,apulsator=hz=0.125",
}

EFFECT_LABELS = {
    "none": "🎵 Normal",
    "bassboost": "🔊 Bass Boost",
    "nightcore": "⚡ Nightcore",
    "slowed": "🐢 Slowed",
    "lofi": "📻 Lofi",
    "8d": "🎧 8D",
}

SPEED_MIN = 0.5
SPEED_MAX = 2.0

SPEED_PRESETS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]


def normalize_effect(effect: str) -> str:
    if not effect:
        return "none"
    effect = str(effect).lower().strip()
    return effect if effect in AUDIO_EFFECTS else "none"


def clamp_speed(value) -> float:
    try:
        speed = float(value)
    except (TypeError, ValueError):
        return 1.0
    return max(SPEED_MIN, min(SPEED_MAX, round(speed, 2)))


def build_audio_filter(effect: str = "none", speed=None) -> str:
    effect = normalize_effect(effect)
    chain = []

    base = AUDIO_EFFECTS.get(effect, "")
    if base:
        chain.append(base)

    if speed is not None:
        sp = clamp_speed(speed)
        if abs(sp - 1.0) > 1e-3:
            chain.append(f"atempo={sp}")

    return ",".join(chain)


def build_ffmpeg_parameters(effect: str = "none", speed=None, seek_position=None):
    parts = []

    if seek_position and seek_position > 0:
        parts.append(f"-ss {int(seek_position)}")

    filt = build_audio_filter(effect, speed)
    if filt:
        parts.append(f"--audio -x:mid -af {filt}")

    return " ".join(parts) if parts else None
