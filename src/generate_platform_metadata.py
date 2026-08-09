"""
generate_platform_metadata.py — asks the LLM to write platform-specific
titles, descriptions, and hashtags for today's finished video, and saves
them to a readable .txt file next to the video output.
"""

import json

from llm_client import call_llm_json

SYSTEM_PROMPT = """You are a social media growth strategist for a US-based
home-fitness content channel. Given today's exercise topic, write
platform-native titles, descriptions, and hashtags.

Rules:
- TikTok/Instagram titles: short, hook-first, 1 emoji max
- YouTube Shorts title: must end with "#shorts"
- YouTube long-form title: benefit-first, under 70 characters
- Facebook post: slightly longer, ends with a question to drive comments
- Every description must end with exactly this line, word for word:
  "{cta_line}"
- Hashtags: 6-10 per platform, mix broad (#homeworkout) and specific
  (tied to the exercise/body part)

Respond with ONLY JSON, no markdown fences, in exactly this shape:
{{
  "titles": {{"tiktok": "...", "youtube_shorts": "...", "youtube_longform": "...", "instagram": "...", "facebook": "..."}},
  "descriptions": {{"tiktok": "...", "youtube": "...", "instagram": "...", "facebook": "..."}},
  "hashtags": {{"tiktok": ["..."], "youtube": ["..."], "instagram": ["..."]}}
}}
"""


def generate_platform_metadata(topic: str, script: dict, config: dict) -> dict:
    system_prompt = SYSTEM_PROMPT.format(cta_line=config["script"]["cta_line"])
    user_prompt = f"Topic: {topic}"
    return call_llm_json(system_prompt, user_prompt)


def write_platform_metadata_file(metadata: dict, out_path: str = "output/platform_metadata.txt"):
    lines = ["PLATFORM METADATA\n" + "=" * 40 + "\n"]
    lines.append("TITLES\n" + "-" * 20)
    for platform, title in metadata["titles"].items():
        lines.append(f"{platform}: {title}")

    lines.append("\nDESCRIPTIONS\n" + "-" * 20)
    for platform, desc in metadata["descriptions"].items():
        lines.append(f"{platform}:\n{desc}\n")

    lines.append("HASHTAGS\n" + "-" * 20)
    for platform, tags in metadata["hashtags"].items():
        lines.append(f"{platform}: {' '.join(tags)}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"[generate_platform_metadata] wrote {out_path}")


if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    result = generate_platform_metadata("Chair Squat for beginners", {}, cfg)
    print(json.dumps(result, indent=2))
