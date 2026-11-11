import cv2
import pandas as pd
import numpy as np
import subprocess

# ==========================================================
# SETTINGS
# ==========================================================

video_path = "Your Video location"
csv_path = "The ball coordinates file"
output_path = "Where you wish to save the overlay video"

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(csv_path)
coords = df[["X", "Y"]].to_numpy()

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError("Could not open video.")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# ==========================================================
# VIDEO WRITER
# ==========================================================

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    output_path,
    fourcc,
    fps,
    (width, height)
)

if not writer.isOpened():
    raise RuntimeError("Could not create output video.")

# ==========================================================
# PROCESS VIDEO
# ==========================================================

frame_number = 0

print("Creating overlay video...")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    if frame_number < len(coords):

        x, y = coords[frame_number]

        if not (np.isnan(x) or np.isnan(y)):

            cv2.circle(
                frame,
                (int(x), int(y)),
                6,
                (0, 255, 0),
                -1
            )

    cv2.putText(
        frame,
        f"Frame: {frame_number + 1}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    writer.write(frame)

    frame_number += 1

    if frame_number % 500 == 0:
        print(f"{frame_number}/{total_frames} frames written...")

# ==========================================================
# CLEAN UP
# ==========================================================

cap.release()
writer.release()
cv2.destroyAllWindows()

print("Finished!")
print(f"Saved to:\n{output_path}")

# ==========================================================
# OPEN IN QUICKTIME
# ==========================================================

subprocess.run(["open", output_path])