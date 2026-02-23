#!/bin/bash
# Extract 13 frames (0.0s to 3.0s at 0.25s intervals) from first 3 seconds of each video
# Then create a single contact sheet per video

SRC="/Users/syedibrahim/Desktop/concept/edited content videos and thier feedback"
OUT="/Users/syedibrahim/Desktop/concept/video-review-frames"

# List of 26 unique videos (excluding duplicates)
videos=(
  "EMD-001_v1.mp4"
  "EMD-002_v1.mp4"
  "Kerala Bulk Cycle.mp4"
  "NXT-001_v1.mp4"
  "NXT-002_v1.mp4"
  "Petrol yelli hakodu.mp4"
  "RAL-001_v1.mp4"
  "SH-002_v1.mp4"
  "SH-003_v1.mp4"
  "SH-004_v1.mp4"
  "SH-006_v1.mp4"
  "TOY-001_v1.mp4"
  "TOY-002_v1.mp4"
  "TOY-003_v1.mp4"
  "TOY-004_v1.mp4"
  "TOY-005_v1.mp4"
  "Toys 5861.mp4"
  "dancing boy.mp4"
  "dirt pocket bike .mp4"
  "doodle e cycle gifts.mp4"
  "kid asking for the gits.mp4"
  "kidnap part 1 .mp4"
  "mother asking gifts - wattson.mp4"
  "night heist police.mp4"
  "self content biuke charg.mp4"
  "yavd bike aa.mp4"
)

for vid in "${videos[@]}"; do
  # Create safe filename (replace spaces and special chars)
  safe=$(echo "$vid" | sed 's/[^a-zA-Z0-9._-]/_/g' | sed 's/.mp4$//')

  echo "Processing: $vid -> $safe"

  # Create subfolder for individual frames
  mkdir -p "$OUT/$safe"

  # Extract 13 frames at 0.25s intervals from 0-3 seconds
  for i in $(seq 0 12); do
    ts=$(echo "scale=2; $i * 0.25" | bc)
    ffmpeg -ss "$ts" -i "$SRC/$vid" -vframes 1 -q:v 2 "$OUT/$safe/frame_${i}.jpg" -y -loglevel error 2>/dev/null
  done

  # Get video dimensions for contact sheet
  width=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$SRC/$vid" 2>/dev/null)
  height=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$SRC/$vid" 2>/dev/null)
  duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC/$vid" 2>/dev/null)

  echo "  Resolution: ${width}x${height}, Duration: ${duration}s"

  # Create contact sheet: 13 frames in a 7x2 grid (last cell empty)
  # Using ffmpeg tile filter for a clean montage
  ffmpeg -i "$OUT/$safe/frame_0.jpg" \
         -i "$OUT/$safe/frame_1.jpg" \
         -i "$OUT/$safe/frame_2.jpg" \
         -i "$OUT/$safe/frame_3.jpg" \
         -i "$OUT/$safe/frame_4.jpg" \
         -i "$OUT/$safe/frame_5.jpg" \
         -i "$OUT/$safe/frame_6.jpg" \
         -i "$OUT/$safe/frame_7.jpg" \
         -i "$OUT/$safe/frame_8.jpg" \
         -i "$OUT/$safe/frame_9.jpg" \
         -i "$OUT/$safe/frame_10.jpg" \
         -i "$OUT/$safe/frame_11.jpg" \
         -i "$OUT/$safe/frame_12.jpg" \
         -filter_complex "
           [0]scale=320:-1[s0];[1]scale=320:-1[s1];[2]scale=320:-1[s2];[3]scale=320:-1[s3];
           [4]scale=320:-1[s4];[5]scale=320:-1[s5];[6]scale=320:-1[s6];[7]scale=320:-1[s7];
           [8]scale=320:-1[s8];[9]scale=320:-1[s9];[10]scale=320:-1[s10];[11]scale=320:-1[s11];
           [12]scale=320:-1[s12];
           [s0][s1][s2][s3][s4][s5][s6]hstack=inputs=7[top];
           [s7][s8][s9][s10][s11][s12][s12]hstack=inputs=7[bot];
           [top][bot]vstack=inputs=2
         " \
         -q:v 2 "$OUT/${safe}_contact.jpg" -y -loglevel error 2>/dev/null

  if [ -f "$OUT/${safe}_contact.jpg" ]; then
    echo "  Contact sheet created: ${safe}_contact.jpg"
  else
    echo "  WARNING: Contact sheet failed for $vid"
  fi

  # Save metadata
  echo "${vid}|${width}|${height}|${duration}" >> "$OUT/metadata.txt"

done

echo ""
echo "=== ALL DONE ==="
echo "Contact sheets in: $OUT"
