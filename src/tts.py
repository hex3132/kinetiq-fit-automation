"""
tts.py — generates ONE continuous voice-over audio file for the whole
video (not one clip per segment) so the narration flows as a single
uninterrupted voice, in a deeper tone via a fixed pitch-down offset.
"""

import asyncio
import os

import edge_tts

# Negative pitch = deeper voice. Applied on top of each character's base voice.
DEEP_PITCH = "-15Hz"
RATE = "-2%"   # very slightly slower reads as more authoritative/deep
VOLUME = "+0%"


async def _generate_one(text, out_path, voice_id, rate, pitch, volume):
    communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(out_path)


def generate_voiceover(script: dict, config: dict, character: dict, out_path="output/audio/full_narration.mp3") -> str:
    """Joins every segment's vo into one continuous script and generates a single audio file."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    full_text = " ".join(seg["vo"].strip() for seg in script["segments"])
    voice_id = character["voice_id"]

    asyncio.run(_generate_one(full_text, out_path, voice_id, RATE, DEEP_PITCH, VOLUME))
    print(f"[tts] wrote continuous narration -> {out_path}")
    return out_path


if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    demo_script = {
        "segments": [
            {"vo": "Today we're breaking down the chair squat."},
            {"vo": "Sit back like there's a chair behind you, then stand tall."},
        ]
    }
    generate_voiceover(demo_script, cfg, cfg["character"]["female"])
