"""
assemble_video.py — builds the final video from per-segment images and
ONE continuous narration audio track. Each image's on-screen duration
is calculated proportionally from its segment's word count against the
full narration's actual spoken length, so timing still lines up even
though there's only one audio file for the whole video.
"""

import os

from moviepy.editor import AudioFileClip, concatenate_videoclips, ImageClip


def _ken_burns_clip(image_path, duration, frame_size, zoom_amount=0.12):
    base = ImageClip(image_path).set_duration(duration)
    base = base.resize(height=int(frame_size[1] * (1 + zoom_amount)))

    def zoom(t):
        return 1 + (zoom_amount * (t / duration))

    zoomed = base.resize(zoom)
    return zoomed.set_position("center")


def _segment_durations(script, total_duration):
    word_counts = [len(seg["vo"].split()) for seg in script["segments"]]
    total_words = sum(word_counts) or 1
    return [max(0.5, total_duration * (wc / total_words)) for wc in word_counts]


def assemble_video(
    script: dict,
    narration_path: str,
    image_paths: list,
    config: dict,
    out_path: str = "output/final_video.mp4",
) -> str:
    v = config["video"]
    frame_size = (v["frame_width"], v["frame_height"])

    narration_audio = AudioFileClip(narration_path)
    total_duration = narration_audio.duration

    durations = _segment_durations(script, total_duration)

    clips = []
    for img_path, duration in zip(image_paths, durations):
        visual = _ken_burns_clip(img_path, duration, frame_size, v.get("zoom_amount", 0.12))
        clips.append(visual)

    final = concatenate_videoclips(clips, method="compose")
    final = final.resize(frame_size)

    # Trim/pad the single narration track to match the assembled video length exactly.
    final = final.set_duration(total_duration)
    final = final.set_audio(narration_audio)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.write_videofile(
        out_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )

    narration_audio.close()
    final.close()

    print(f"[assemble_video] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    print("Run via main.py — this module needs script/narration/image outputs from earlier steps.")
