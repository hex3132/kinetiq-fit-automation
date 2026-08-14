"""
generate_flow_prompts.py — builds a Google Flow prompt as structured
JSON, one scene per script segment (10 scenes), each with an explicit
"emotion" field, so the same coach character fully performs one
complete exercise across the video with clear emotional direction
per scene.
"""

import json

SCENE_TITLES = [
    "Hook",
    "Exercise Introduction",
    "Starting Position",
    "The Movement",
    "Breathing & Tempo",
    "Common Mistake",
    "Correct Form Fix",
    "Why It Works",
    "Motivation",
    "Outro / Call to Action",
]


def build_flow_prompt_json(script: dict, config: dict, character: dict) -> dict:
    set_desc = config["character"]["shared_set_description"].strip()
    char_desc = character["visual_description"].strip()
    char_name = character["display_name"]
    seconds_per_segment = config["script"]["seconds_per_segment"]
    total_seconds = seconds_per_segment * len(script["segments"])

    full_narration = " ".join(seg["vo"].strip() for seg in script["segments"])

    scene_sequence = []
    for i, seg in enumerate(script["segments"]):
        title = SCENE_TITLES[i] if i < len(SCENE_TITLES) else f"Scene {i + 1}"
        scene_sequence.append({
            "scene": i + 1,
            "title": title,
            "duration": f"{seconds_per_segment} seconds",
            "character": char_name,
            "character_description": char_desc,
            "action": f"{char_name} is fully visible, {seg['visual']}, completing full clean repetitions of the movement without being cut off mid-motion",
            "setting": set_desc,
            "camera": "steady vertical framing, smooth continuous motion, no jarring cuts",
            "emotion": seg["emotion"],
            "emotion_direction": _emotion_direction(seg["emotion"]),
        })

    return {
        "video_type": "cinematic home-fitness coaching demonstration",
        "topic": script.get("topic", "Home workout"),
        "exercise_name": script.get("exercise_name", ""),
        "target_area": script.get("target_area", ""),
        "duration": f"{total_seconds} seconds",
        "aspect_ratio": "9:16",
        "style": "photorealistic cinematic fitness content",
        "quality": "ultra detailed 4K",
        "camera_style": "smooth continuous tracking, steady vertical framing",
        "character_consistency_note": "Use the exact same character_description string, unchanged, in every scene below — this keeps the same coach appearing throughout.",
        "environment": {
            "background": set_desc,
            "lighting": "warm natural daylight",
            "atmosphere": "clean, motivating, instructional home-fitness content",
        },
        "main_subject": {
            "type": f"{char_name}, a fitness coach",
            "description": char_desc,
            "pose": "fully visible, full body in frame, performing the complete exercise",
            "visibility": "fully visible throughout, never cropped mid-repetition",
        },
        "scene_sequence": scene_sequence,
        "voice_over": {
            "delivery": "one single continuous take, deep calm confident coaching tone, no repeated words or filler phrases, no pauses between scenes",
            "full_script": full_narration,
        },
        "render_keywords": [
            "photorealistic fitness coaching",
            "cinematic home workout content",
            "smooth continuous motion",
            "one continuous exercise demonstration",
            "consistent character across scenes",
            "vertical short-form video",
            "clear emotional pacing scene to scene",
        ],
    }


def _emotion_direction(emotion: str) -> str:
    directions = {
        "energetic": "upbeat, high energy, quick pacing",
        "instructional": "clear, measured, precise delivery",
        "warning": "slightly urgent, cautionary tone",
        "warm": "gentle, friendly, reassuring",
        "confident": "steady, assured, grounded",
        "inviting": "welcoming, open, friendly",
        "encouraging": "supportive, uplifting, motivating",
        "calm": "relaxed, slow, steady breathing tone",
    }
    return directions.get(emotion, "neutral, clear delivery")


def write_flow_prompt_file(script: dict, config: dict, character: dict, out_path: str = "output/flow_prompt.json") -> str:
    data = build_flow_prompt_json(script, config, character)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[generate_flow_prompts] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Import and call write_flow_prompt_file(...) from main.py.")
