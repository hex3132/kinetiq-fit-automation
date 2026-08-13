"""
main.py — orchestrator. Calls every step in order, each step's output
feeding the next step's input. Non-essential steps (metadata, flow
prompts, Drive upload) are wrapped in try/except so a failure there
doesn't throw away a video that already finished rendering.
"""

import sys
import traceback
from datetime import date

import yaml

from fetch_topics import get_best_topic
from research_topic import research_topic
from generate_script import generate_script
from tts import generate_voiceovers
from generate_ai_visuals import generate_ai_visuals
from assemble_video import assemble_video
from generate_platform_metadata import generate_platform_metadata, write_platform_metadata_file
from generate_flow_prompts import write_flow_prompt_file


def pick_todays_character(config):
    day_index = date.today().timetuple().tm_yday
    key = "female" if day_index % 2 == 0 else "male"
    return key, config["character"][key]


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    character_key, character = pick_todays_character(config)
    print(f"[main] Today's character: {character['display_name']} ({character_key})")

    topic = get_best_topic()
    research_notes = research_topic(topic)
    script = generate_script(topic, config, research_notes, character)
    script["topic"] = topic
    audio_paths = generate_voiceovers(script, config, character)
    image_paths = generate_ai_visuals(script, config, character)
    video_path = assemble_video(script, audio_paths, image_paths, config)

    date_str = date.today().isoformat()
    metadata_path = "output/platform_metadata.txt"
    flow_prompt_path = None

    try:
        metadata = generate_platform_metadata(topic, script, config)
        write_platform_metadata_file(metadata, metadata_path)
    except Exception as e:
        print(f"[main] Platform metadata generation failed (non-fatal, skipping): {e}")
        metadata_path = None

    try:
        flow_prompt_path = write_flow_prompt_file(script, config, character)
    except Exception as e:
        print(f"[main] Flow prompt generation failed (non-fatal, skipping): {e}")

    try:
        import os
        if os.environ.get("GOOGLE_REFRESH_TOKEN") and os.environ.get("GDRIVE_FOLDER_ID"):
            from upload_drive import upload_daily_outputs
            upload_daily_outputs(
                video_path,
                metadata_path or video_path,
                os.environ["GDRIVE_FOLDER_ID"],
                date_str,
                flow_prompt_path=flow_prompt_path,
            )
        else:
            print("[main] Drive credentials not set — skipping upload, files left in /output.")
    except Exception as e:
        print(f"[main] Drive upload failed (non-fatal): {e}")

    print(f"[main] Done. Video: {video_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("[main] Pipeline failed:")
        traceback.print_exc()
        sys.exit(1)
