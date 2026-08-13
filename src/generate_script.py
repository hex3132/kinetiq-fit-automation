"""
generate_script.py — turns a topic + research notes into ONE continuous,
flowing script for a single complete exercise, spoken by one character
from start to finish with no repeated phrases and no awkward segment
breaks in the narration.
"""

from llm_client import call_llm_json

SYSTEM_PROMPT_TEMPLATE = """You are an expert fitness scriptwriter writing
a SINGLE continuous voice-over script for a {seconds_total}-second
vertical video. One character, {character_name}, fully demonstrates and
completes ONE exercise from start to finish — not multiple exercises,
not a cut-up list of tips.

Character appearance (do not describe this yourself, handled
separately): {character_description}. Setting: {set_description}.

Write the narration as ONE continuous, natural, flowing script — as if
a single person is speaking without pausing between topics. Rules:
- Deep, calm, confident, authoritative coaching tone. Not hype-shouty,
  not repetitive filler ("let's go", "come on") used more than once.
- NEVER repeat the same word, phrase, or sentence structure twice in
  the whole script. Every sentence must add new information.
- Cover, in this order, as ONE unbroken narration: a brief hook, the
  exercise name and what it targets, step-by-step instruction on
  performing it correctly, the most common mistake and how to fix it,
  why it works / the benefit, and end with this EXACT closing line,
  word for word, as the final sentence:
  "{cta_line}"
- The character must be shown fully performing complete repetitions of
  the exercise throughout — never cut away before the movement finishes.

Break this single narration into {segments} segments ONLY for the
purpose of matching visuals — the spoken words must still read as one
uninterrupted script when all segments are joined in order. Each
segment needs:
  - "visual": what the coach is physically doing on screen during this
    part (physical action only)
  - "vo": this segment's slice of the continuous narration, roughly
    {words_min}-{words_max} words
  - "emotion": one of "energetic", "instructional", "warning", "warm",
    "confident", "inviting"

Use these researched facts if relevant, do not contradict them:
{research_notes}

Respond with ONLY a JSON object, no markdown fences, in exactly this
shape:
{{"topic": "...", "exercise_name": "...", "target_area": "...",
"segments": [{{"visual": "...", "vo": "...", "emotion": "..."}}]}}
"""


def build_system_prompt(topic, config, research_notes, character):
    s = config["script"]
    return SYSTEM_PROMPT_TEMPLATE.format(
        seconds_total=s["segments"] * s["seconds_per_segment"],
        character_name=character["display_name"],
        character_description=character["visual_description"],
        set_description=config["character"]["shared_set_description"],
        segments=s["segments"],
        words_min=s["words_per_segment_min"],
        words_max=s["words_per_segment_max"],
        cta_line=s["cta_line"],
        research_notes=research_notes or "(no additional research notes available)",
    )


def _validate_script(script, config):
    all_words = []
    for seg in script["segments"]:
        all_words.extend(seg["vo"].lower().split())
    seen = set()
    dupes = set()
    for w in all_words:
        clean = w.strip(".,!?\"'")
        if len(clean) > 4:
            if clean in seen:
                dupes.add(clean)
            seen.add(clean)
    if dupes:
        print(f"WARNING: repeated significant words detected: {dupes}")


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
