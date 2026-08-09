"""
assemble_video.py — the final step: turns the per-segment images + audio
into one finished vertical video. Each image is shown for exactly as long
as its matching voiceover clip lasts (read from the audio file itself, so
segments are never cut short or stretched to a guessed length), with a
slow Ken Burns zoom for visual movement.
"""

import os

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    ImageClip,
    concatenate_videoclips,
)


def _ken_burns_clip(image_path, duration, frame_size, zoom_amount=0.12):
    base = ImageClip(image_path).set_duration(duration)
    base = base.resize(height=int(frame_size[1] * (1 + zoom_amount)))

    def zoom(t):
        return 1 + (zoom_amount * (t / duration))

    zoomed = base.resize(zoom)
    return zoomed.set_position("center")


def assemble_video(
    script: dict,
    audio_paths: list,
    image_paths: list,
    config: dict,
    out_path: str = "output/final_video.mp4",
) -> str:
    v = config["video"]
    frame_size = (v["frame_width"], v["frame_height"])

    clips = []
    audio_clips = []

    for img_path, audio_path in zip(image_paths, audio_paths):
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration  # actual spoken length, not a guess
        visual = _ken_burns_clip(img_path, duration, frame_size, v.get("zoom_amount", 0.12))
        visual = visual.set_audio(audio_clip)
        clips.append(visual)
        audio_clips.append(audio_clip)

    final = concatenate_videoclips(clips, method="compose")
    final = final.resize(frame_size)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.write_videofile(
        out_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )

    for c in audio_clips:
        c.close()
    final.close()

    print(f"[assemble_video] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Run via main.py — this module needs script/audio/image outputs from earlier steps.")
