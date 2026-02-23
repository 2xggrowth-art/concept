#!/usr/bin/env python3
"""Transcribe the first 5 seconds of each video using Whisper."""
import os
import subprocess
import whisper
import json

SRC = "/Users/syedibrahim/Desktop/concept/edited content videos and thier feedback"
OUT = "/Users/syedibrahim/Desktop/concept/video-review-frames"
AUDIO_DIR = os.path.join(OUT, "audio_clips")
os.makedirs(AUDIO_DIR, exist_ok=True)

videos = [
    "EMD-001_v1.mp4",
    "EMD-002_v1.mp4",
    "Kerala Bulk Cycle.mp4",
    "NXT-001_v1.mp4",
    "NXT-002_v1.mp4",
    "Petrol yelli hakodu.mp4",
    "RAL-001_v1.mp4",
    "SH-002_v1.mp4",
    "SH-003_v1.mp4",
    "SH-004_v1.mp4",
    "SH-006_v1.mp4",
    "TOY-001_v1.mp4",
    "TOY-002_v1.mp4",
    "TOY-003_v1.mp4",
    "TOY-004_v1.mp4",
    "TOY-005_v1.mp4",
    "Toys 5861.mp4",
    "dancing boy.mp4",
    "dirt pocket bike .mp4",
    "doodle e cycle gifts.mp4",
    "kid asking for the gits.mp4",
    "kidnap part 1 .mp4",
    "mother asking gifts - wattson.mp4",
    "night heist police.mp4",
    "self content biuke charg.mp4",
    "yavd bike aa.mp4",
]

# Load whisper model (turbo for speed + quality balance)
print("Loading Whisper turbo model...")
model = whisper.load_model("turbo")
print("Model loaded.")

results = {}

for vid in videos:
    src_path = os.path.join(SRC, vid)
    safe = vid.replace(" ", "_").replace(".", "_").replace("(", "").replace(")", "")
    safe = safe.rsplit("_mp4", 1)[0] if safe.endswith("_mp4") else safe.replace(".mp4", "")
    audio_path = os.path.join(AUDIO_DIR, f"{safe}_5sec.wav")

    print(f"\nProcessing: {vid}")

    # Extract first 5 seconds of audio
    cmd = [
        "ffmpeg", "-i", src_path,
        "-t", "5",
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y", "-loglevel", "error"
    ]
    subprocess.run(cmd, check=False)

    if not os.path.exists(audio_path):
        print(f"  WARNING: Could not extract audio from {vid}")
        results[vid] = {"text": "[NO AUDIO EXTRACTED]", "language": "unknown"}
        continue

    # Transcribe with whisper
    try:
        result = model.transcribe(audio_path, language=None)
        text = result.get("text", "").strip()
        lang = result.get("language", "unknown")
        print(f"  Language: {lang}")
        print(f"  Text: {text}")
        results[vid] = {"text": text, "language": lang}
    except Exception as e:
        print(f"  ERROR: {e}")
        results[vid] = {"text": f"[ERROR: {e}]", "language": "unknown"}

# Save all transcriptions
output_path = os.path.join(OUT, "transcriptions.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n=== ALL TRANSCRIPTIONS SAVED to {output_path} ===")
