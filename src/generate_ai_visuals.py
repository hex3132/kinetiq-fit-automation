"""
generate_ai_visuals.py — generates one still image per segment via
Pollinations. The character's fixed visual_description is appended to
every segment prompt so the coach looks the same across the whole
video — this is the character-consistency mechanism for this pipeline.
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
