"""
generate_script.py — turns a topic + research notes into a structured,
segment-by-segment script: what's shown, what's said, and what emotion
it's said with. This is the backbone every other step (voiceover, images,
Flow prompts, metadata) is built from.
"""

from llm_client import call_llm_json

SYSTEM_PROMPT_TEMPLATE = """You are an expert short-form fitness content scriptwriter.

You are writing the script for a {seconds_total}-second vertical video
featuring a fitness coach character named {character_name}. Character
appearance (do not describe this yourself, it is handled separately):
{character_description}. Setting: {set_description}.

Write EXACTLY {segments} segments, each covering {seconds_per_segment}
seconds. Each segment needs:
  - "visual": a short plain description of what the coach is doing on
    screen in this segment (physical action only, no camera jargon)
  - "vo": the voice-over line spoken during this segment, between
    {words_min} and {words_max} words
  - "emotion": one of "energetic", "instructional", "warning", "warm",
    "confident", "inviting"

Segment structure to follow in order:
  1. Intro/hook — greet the viewer with energy
  2. Exercise demo — clear instruction on how to do the move
  3. Common mistake — describe the mistake people make (warning tone)
  4. Correct form fix — describe the fix (confident tone)
  5. Quick benefit/why-it-works — warm, motivating
  6. Outro — this EXACT line, word for word, must be the "vo" value:
     "{cta_line}"

Use these researched facts if relevant, do not contradict them:
{research_notes}

Respond with ONLY a JSON object, no markdown fences, in exactly this shape:
{{"topic": "...", "segments": [{{"visual": "...", "vo": "...", "emotion": "..."}}]}}
"""


def build_system_prompt(topic, config, research_notes, character):
    s = config["script"]
    return SYSTEM_PROMPT_TEMPLATE.format(
        seconds_total=s["segments"] * s["seconds_per_segment"],
        character_name=character["display_name"],
        character_description=character["visual_description"],
        set_description=config["character"]["shared_set_description"],
        segments=s["segments"],
        seconds_per_segment=s["seconds_per_segment"],
        words_min=s["words_per_segment_min"],
        words_max=s["words_per_segment_max"],
        cta_line=s["cta_line"],
        research_notes=research_notes or "(no additional research notes available)",
    )


def _validate_script(script, config):
    s = config["script"]
    for i, seg in enumerate(script["segments"]):
        word_count = len(seg["vo"].split())
        if not (s["words_per_segment_min"] <= word_count <= s["words_per_segment_max"]):
            print(
                f"WARNING: segment {i} has {word_count} words "
                f"(expected {s['words_per_segment_min']}-{s['words_per_segment_max']})"
            )


def generate_script(topic: str, config: dict, research_notes: str, character: dict) -> dict:
    system_prompt = build_system_prompt(topic, config, research_notes, character)
    user_prompt = f"Topic: {topic}"
    script = call_llm_json(system_prompt, user_prompt)
    _validate_script(script, config)
    return script


if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    result = generate_script(
        "Chair Squat for beginners", cfg, "", cfg["character"]["female"]
    )
    print(result)
