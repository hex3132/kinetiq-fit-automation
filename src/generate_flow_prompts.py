"""
generate_flow_prompts.py — OPTIONAL step. The pipeline already produces a
finished video without Google Flow. This file exists only if you also
want a Flow-ready prompt file for a specific segment — e.g. to
re-generate one segment at higher visual quality by hand in Flow. Not
called by main.py by default; call it manually if you want it.
"""

import json


def build_flow_prompt_for_segment(segment: dict, character: dict, set_description: str, duration: int) -> dict:
    return {
        "character": character["display_name"],
        "duration_seconds": duration,
        "shot": "medium full-body shot, side angle",
        "setting": set_description,
        "character_description": character["visual_description"],
        "action": segment["visual"],
        "camera": "steady framing, no cuts, continuous motion",
        "lighting": "bright clean daylight",
        "mood": segment["emotion"],
    }


def write_flow_prompts_file(script: dict, config: dict, character: dict, out_path: str = "output/flow_prompts.json"):
    set_desc = config["character"]["shared_set_description"]
    duration = config["script"]["seconds_per_segment"]
    prompts = [
        build_flow_prompt_for_segment(seg, character, set_desc, duration)
        for seg in script["segments"]
    ]
    with open(out_path, "w") as f:
        json.dump(prompts, f, indent=2)
    print(f"[generate_flow_prompts] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Optional module — see docstring. Call write_flow_prompts_file() manually if needed.")
