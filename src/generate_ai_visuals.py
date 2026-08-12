"""
generate_ai_visuals.py — generates one still image per segment via
Pollinations (free, no API key, just an HTTP GET with the prompt in the
URL). The character's fixed visual_description is appended to every
segment prompt so the coach looks the same across the whole video —
this is the character-consistency mechanism for this pipeline.
"""

import os
import time
import urllib.parse

import requests

POLLINATIONS_BASE = "https://gen.pollinations.ai/image"


def _build_url(prompt, width, height, seed=None):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}/{encoded_prompt}?width={width}&height={height}"
    if seed is not None:
        url += f"&seed={seed}"
    return url


def _download_image(url, out_path, retries=3):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return out_path
        except Exception as e:
            print(f"[generate_ai_visuals] attempt {attempt}/{retries} failed: {e}")
            time.sleep(3)
    raise RuntimeError(f"Image generation failed after {retries} attempts: {url}")


def generate_ai_visuals(script: dict, config: dict, character: dict, out_dir="output/images") -> list:
    os.makedirs(out_dir, exist_ok=True)
    v = config["video"]
    set_desc = config["character"]["shared_set_description"]

    # Fixed seed per character keeps Pollinations' output closer in style
    # across segments than leaving it random.
    seed = abs(hash(character["display_name"])) % 100000

    paths = []
    for i, seg in enumerate(script["segments"]):
        prompt = (
            f"{character['visual_description']}, {seg['visual']}, "
            f"{set_desc}, photorealistic, cinematic lighting, vertical composition"
        )
        url = _build_url(prompt, v["frame_width"], v["frame_height"], seed=seed)
        out_path = os.path.join(out_dir, f"segment_{i:02d}.jpg")
        _download_image(url, out_path)
        print(f"[generate_ai_visuals] segment {i} -> {out_path}")
        paths.append(out_path)

    return paths


if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    demo_script = {"segments": [{"visual": "standing, greeting the camera with a wave"}]}
    generate_ai_visuals(demo_script, cfg, cfg["character"]["female"])
