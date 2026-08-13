"""
generate_flow_prompts.py — builds a human-readable Google Flow prompt
text file for today's character + exercise. Each segment becomes a
natural-language prompt block you can paste directly into Google Flow,
with the character description kept identical across every block so
the same coach appears in every generated clip.
"""


def build_flow_prompt_text(script: dict, config: dict, character: dict) -> str:
    set_desc = config["character"]["shared_set_description"].strip()
    char_desc = character["visual_description"].strip()
    char_name = character["display_name"]

    lines = []
    lines.append(f"GOOGLE FLOW PROMPTS — {char_name}")
    lines.append(f"Topic: {script.get('topic', 'Home workout')}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Keep the CHARACTER line identical in every prompt below —")
    lines.append("this is what keeps the same coach appearing across clips.")
    lines.append("")
    lines.append(f"CHARACTER: {char_desc}")
    lines.append(f"SETTING: {set_desc}")
    lines.append("")
    lines.append("=" * 60)

    scene_labels = [
        "SCENE 1 — Intro / Hook",
        "SCENE 2 — Exercise Demo (step-by-step)",
        "SCENE 3 — Common Mistake",
        "SCENE 4 — Correct Form Fix",
        "SCENE 5 — Benefit / Why It Works",
        "SCENE 6 — Outro / Call to Action",
    ]

    for i, seg in enumerate(script["segments"]):
        label = scene_labels[i] if i < len(scene_labels) else f"SCENE {i + 1}"
        lines.append("")
        lines.append(label)
        lines.append("-" * len(label))
        lines.append(
            f"A cinematic vertical shot in {set_desc}. "
            f"{char_name} — {char_desc} — {seg['visual']}. "
            f"Mood: {seg['emotion']}. Smooth continuous motion, natural lighting, "
            f"no on-screen text."
        )
        lines.append(f"[Spoken line for this scene: \"{seg['vo']}\"]")

    lines.append("")
    lines.append("=" * 60)
    lines.append("HOW TO USE: Copy each SCENE block into Google Flow one at a")
    lines.append("time, generating one clip per scene. Keep the CHARACTER line")
    lines.append("unchanged between scenes for visual consistency, then stitch")
    lines.append("the resulting clips together in order.")

    return "\n".join(lines)


def write_flow_prompt_file(script: dict, config: dict, character: dict, out_path: str = "output/flow_prompt.txt") -> str:
    text = build_flow_prompt_text(script, config, character)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[generate_flow_prompts] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Import and call write_flow_prompt_file(...) from main.py.")
