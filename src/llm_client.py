"""
llm_client.py — the one place every other file goes through to talk to an LLM.

Why centralized: generate_script.py, generate_flow_prompts.py, and
generate_platform_metadata.py all need "give me JSON back from a prompt" —
writing that logic three times would mean fixing the same bug three times
later. This file also owns the provider-fallback logic, so if Google
renames a model (it happens), you only fix it here.
"""

import json
import os
import time

import requests

GEMINI_MODEL_CANDIDATES = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-pro-latest",
]

GROQ_MODEL_CANDIDATES = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
]


def clean_json_text(raw: str) -> str:
    """Strip markdown code fences the model sometimes adds around JSON."""
    return (
        raw.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )


def _call_gemini(system_prompt, user_prompt, api_key, json_mode):
    generation_config = {"temperature": 0.9}
    if json_mode:
        generation_config["responseMimeType"] = "application/json"

    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": generation_config,
    }

    last_error = None
    for model_name in GEMINI_MODEL_CANDIDATES:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={api_key}"
        )
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 404:
                continue  # this model name doesn't exist for this API version — try the next
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.HTTPError as e:
            last_error = e
            continue
    raise RuntimeError(f"All Gemini model candidates failed. Last error: {last_error}")


def _call_groq(system_prompt, user_prompt, api_key, json_mode):
    last_error = None
    for model_name in GROQ_MODEL_CANDIDATES:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.9,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=60,
            )
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            last_error = e
            continue
    raise RuntimeError(f"All Groq model candidates failed. Last error: {last_error}")


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = True):
    """
    Sends a system+user prompt to whichever provider is configured via
    environment variables and returns the raw text response.

    Env vars:
      LLM_PROVIDER — "gemini" (default) or "groq"
      LLM_API_KEY  — required, no default (missing key should be a loud
                     error, not a silent failure)
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    api_key = os.environ["LLM_API_KEY"]

    if provider == "gemini":
        raw = _call_gemini(system_prompt, user_prompt, api_key, json_mode)
    elif provider == "groq":
        raw = _call_groq(system_prompt, user_prompt, api_key, json_mode)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    return clean_json_text(raw) if json_mode else raw


def call_llm_json(system_prompt: str, user_prompt: str, retries: int = 2) -> dict:
    """Convenience wrapper: call_llm + json.loads, with one retry on parse failure."""
    last_error = None
    for attempt in range(retries + 1):
        raw = call_llm(system_prompt, user_prompt, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = e
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    pass
            time.sleep(2)
    raise RuntimeError(f"LLM did not return valid JSON after {retries + 1} attempts: {last_error}")


if __name__ == "__main__":
    # Quick manual test: python src/llm_client.py
    result = call_llm_json(
        "Respond with ONLY JSON: {\"greeting\": \"...\"}",
        "Say hello to a fitness content creator.",
    )
    print(result)
