"""
generate_script.py — turns a topic + research notes into ONE continuous,
flowing script for a single complete exercise, spoken by one character
from start to finish with no repeated phrases, structured across a
full 10-part tutorial arc.
"""

from llm_client import call_llm_json

SYSTEM_PROMPT_TEMPLATE = """You are an expert fitness scriptwriter writing
a SINGLE continuous voice-over script for a {seconds_total}-second
vertical video. One character, {character_name}, fully demonstrates and
completes ONE exercise from start to finish — not multiple exercises.

Character appearance (do not describe this yourself, handled
separately): {character_description}. Setting: {set_description}.

Write the narration as ONE continuous, natural, flowing script — as if
a single person is speaking without pausing between topics. Rules:
- Deep, calm, confident, authoritative coaching tone. Not hype-shouty.
  Do not reuse the same filler phrase ("let's go", "come on") more than once.
- NEVER repeat the same word, phrase, or sentence structure twice in
  the whole script. Every sentence must add new information.
- The character must be shown fully performing complete repetitions of
  the exercise throughout — never cut away before the movement finishes.

Break this into EXACTLY {segments} segments, following this narrative arc:
  1. Hook — grab attention in the first line
  2. Introduce the exercise name and what it targets
  3. Step-by-step instruction, part 1 (starting position)
  4. Step-by-step instruction, part 2 (the movement)
  5. Step-by-step instruction, part 3 (breathing / tempo)
  6. Common mistake people make
  7. How to fix that mistake / correct form cue
  8. Why this exercise works / the benefit
  9. Motivational encouragement to keep going
  10. Outro — this EXACT line, word for word, must be the final "vo" value:
      "{cta_line}"

Each segment needs:
  - "visual": what the coach is physically doing on screen during this
    part (physical action only)
  - "vo": this segment's slice of the continuous narration, roughly
    {words_min}-{words_max} words
  - "emotion": one of "energetic", "instructional", "warning", "warm",
    "confident", "inviting", "encouraging", "calm"

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

    expected = config["script"]["segments"]
    actual = len(script["segments"])
    if actual != expected:
        print(f"WARNING: expected {expected} segments, got {actual}")


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
