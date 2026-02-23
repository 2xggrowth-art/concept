#!/usr/bin/env python3
"""Extract first 3 seconds at 4fps and create contact sheets using PIL."""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

SRC = "/Users/syedibrahim/Desktop/concept/edited content videos and thier feedback"
OUT = "/Users/syedibrahim/Desktop/concept/video-review-frames"
os.makedirs(OUT, exist_ok=True)

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

def safe_name(vid):
    return vid.replace(" ", "_").replace("(", "").replace(")", "").replace(".mp4", "")

def get_duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "csv=p=0", path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

def extract_frames_fps(src_path, out_dir, safe):
    """Extract first 3 seconds at 4fps = 12 frames using fps filter."""
    frame_dir = os.path.join(out_dir, safe)
    os.makedirs(frame_dir, exist_ok=True)

    cmd = [
        "ffmpeg", "-i", src_path,
        "-t", "3",
        "-vf", "fps=4",
        "-q:v", "2",
        os.path.join(frame_dir, "frame_%03d.jpg"),
        "-y", "-loglevel", "error"
    ]
    subprocess.run(cmd, check=False)

    # List extracted frames sorted
    frames = sorted([f for f in os.listdir(frame_dir) if f.startswith("frame_") and f.endswith(".jpg")])
    return [os.path.join(frame_dir, f) for f in frames]

def create_contact_sheet(frame_paths, output_path, vid_name, duration):
    """Create a labeled contact sheet from frames."""
    if not frame_paths:
        print(f"  No frames to create contact sheet")
        return False

    # Load all frames
    images = []
    for fp in frame_paths:
        try:
            img = Image.open(fp)
            images.append(img)
        except:
            pass

    if not images:
        return False

    # Thumbnail size (maintain aspect ratio, fit in 250px width)
    thumb_w = 250
    orig_w, orig_h = images[0].size
    thumb_h = int(thumb_w * orig_h / orig_w)

    # Grid: frames in a single row or 2 rows
    n = len(images)
    cols = min(n, 6)
    rows = (n + cols - 1) // cols

    # Padding and label height
    pad = 5
    label_h = 30
    title_h = 40

    sheet_w = cols * (thumb_w + pad) + pad
    sheet_h = title_h + rows * (thumb_h + label_h + pad) + pad

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    # Title
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        font = ImageFont.load_default()
        small_font = font

    title = f"{vid_name}  |  Duration: {duration:.1f}s  |  First 3 seconds"
    draw.text((pad, 8), title, fill="black", font=font)

    # Place frames
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols

        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        x = pad + col * (thumb_w + pad)
        y = title_h + pad + row * (thumb_h + label_h + pad)

        sheet.paste(thumb, (x, y))

        # Timestamp label
        ts = idx * 0.25  # 4fps = 0.25s per frame
        label = f"{ts:.2f}s"
        draw.text((x + thumb_w // 2 - 15, y + thumb_h + 2), label, fill="black", font=small_font)

    sheet.save(output_path, quality=90)
    return True

# Process all videos
print("=" * 60)
print("EXTRACTING FRAMES + CREATING CONTACT SHEETS")
print("=" * 60)

for i, vid in enumerate(videos):
    src_path = os.path.join(SRC, vid)
    safe = safe_name(vid)

    print(f"\n[{i+1}/{len(videos)}] {vid}")

    if not os.path.exists(src_path):
        print(f"  FILE NOT FOUND: {src_path}")
        continue

    duration = get_duration(src_path)
    print(f"  Duration: {duration:.1f}s")

    # Extract frames
    frame_paths = extract_frames_fps(src_path, OUT, safe)
    print(f"  Extracted {len(frame_paths)} frames")

    # Create contact sheet
    contact_path = os.path.join(OUT, f"{safe}_contact.jpg")
    ok = create_contact_sheet(frame_paths, contact_path, vid, duration)
    if ok:
        print(f"  Contact sheet: {safe}_contact.jpg")
    else:
        print(f"  WARNING: Contact sheet failed")

print("\n" + "=" * 60)
print("ALL DONE")
print("=" * 60)
