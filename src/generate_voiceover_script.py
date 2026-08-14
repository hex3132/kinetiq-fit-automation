"""
generate_voiceover_script.py — writes a standalone, human-readable
scene-by-scene voice-over script file with emotion direction for each
scene, separate from the Flow JSON — handy for a human narrator, a
video editor, or a client hand-out.
"""


def build_voiceover_text(script: dict, character: dict) -> str:
    char_name = character["display_name"]
    lines = []
    lines.append(f"VOICE-OVER SCRIPT — {char_name}")
    lines.append(f"Exercise: {script.get('exercise_name', script.get('topic', ''))}")
    lines.append(f"Target area: {script.get('target_area', '')}")
    lines.append("=" * 60)
    lines.append("")

    for i, seg in enumerate(script["segments"]):
        lines.append(f"SCENE {i + 1}  —  Emotion: {seg['emotion'].upper()}")
        lines.append("-" * 40)
        lines.append(f"Visual: {seg['visual']}")
        lines.append(f"Line: \"{seg['vo']}\"")
        lines.append("")

    lines.append("=" * 60)
    lines.append("FULL CONTINUOUS SCRIPT (for one uninterrupted take):")
    lines.append("")
    lines.append(" ".join(seg["vo"].strip() for seg in script["segments"]))

    return "\n".join(lines)


def write_voiceover_script_file(script: dict, character: dict, out_path: str = "output/voiceover_script.txt") -> str:
    text = build_voiceover_text(script, character)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[generate_voiceover_script] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Import and call write_voiceover_script_file(...) from main.py.")
