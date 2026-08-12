import os
import time
import urllib.parse

import requests

POLLINATIONS_BASE = "https://gen.pollinations.ai/image"


def _build_url(prompt, width, height, seed=None):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}/{encoded_prompt}?width={width}&height={height}&model=flux"
    if seed is not None:
        url += f"&seed={seed}"
    api_key = os.environ.get("POLLINATIONS_API_KEY")
    if api_key:
        url += f"&key={api_key}"
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


def generate_ai_visuals(script, config, character, out_dir="output/images"):
    os.makedirs(out_dir, exist_ok=True)
    v = config["video"]
    set_desc = config["character"]["shared_set_description"]

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
