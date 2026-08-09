"""
tts.py — turns each script segment's "vo" text into an audio file, with
rate/pitch/volume nudged per the segment's "emotion" tag. Uses edge-tts
(free, no API key — uses Microsoft's public neural voices).
"""

import asyncio
import os
import re

import edge_tts

EMOTION_ADJUSTMENTS = {
    "energetic": {"rate_delta": 10, "pitch_delta": 4, "volume_delta": 8},
    "instructional": {"rate_delta": 0, "pitch_delta": 0, "volume_delta": 0},
    "warning": {"rate_delta": 5, "pitch_delta": -3, "volume_delta": 5},
    "confident": {"rate_delta": 2, "pitch_delta": 2, "volume_delta": 3},
    "warm": {"rate_delta": -8, "pitch_delta": -2, "volume_delta": -5},
    "inviting": {"rate_delta": -5, "pitch_delta": 0, "volume_delta": 0},
}

BASE_RATE = "+0%"
BASE_PITCH = "+0Hz"
BASE_VOLUME = "+0%"


def _parse_signed_unit(value: str, unit: str) -> int:
    match = re.search(r"([+-]?\d+)", value)
    return int(match.group(1)) if match else 0


def _apply_emotion(base_rate, base_pitch, base_volume, emotion):
    adj = EMOTION_ADJUSTMENTS.get(emotion, EMOTION_ADJUSTMENTS["instructional"])

    rate_num = _parse_signed_unit(base_rate, "%") + adj["rate_delta"]
    pitch_num = _parse_signed_unit(base_pitch, "Hz") + adj["pitch_delta"]
    volume_num = _parse_signed_unit(base_volume, "%") + adj["volume_delta"]

    rate_str = f"{'+' if rate_num >= 0 else ''}{rate_num}%"
    pitch_str = f"{'+' if pitch_num >= 0 else ''}{pitch_num}Hz"
    volume_str = f"{'+' if volume_num >= 0 else ''}{volume_num}%"
    return rate_str, pitch_str, volume_str


async def _generate_one(text, out_path, voice_id, rate, pitch, volume):
    communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(out_path)


def generate_voiceovers(script: dict, config: dict, character: dict, out_dir="output/audio") -> list:
    """Generates one mp3 per segment, returns list of file paths in order."""
    os.makedirs(out_dir, exist_ok=True)
    voice_id = character["voice_id"]
    paths = []

    for i, seg in enumerate(script["segments"]):
        rate, pitch, volume = _apply_emotion(BASE_RATE, BASE_PITCH, BASE_VOLUME, seg["emotion"])
        out_path = os.path.join(out_dir, f"segment_{i:02d}.mp3")
        asyncio.run(_generate_one(seg["vo"], out_path, voice_id, rate, pitch, volume))
        print(f"[tts] segment {i} ({seg['emotion']}) -> {out_path}")
        paths.append(out_path)

    return paths


if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    demo_script = {
        "segments": [
            {"visual": "coach greets camera", "vo": "Hey! Ready to feel the burn today? Let's go!", "emotion": "energetic"},
        ]
    }
    generate_voiceovers(demo_script, cfg, cfg["character"]["female"])
