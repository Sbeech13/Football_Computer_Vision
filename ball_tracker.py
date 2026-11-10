import cv2
import pandas as pd
import numpy as np
import os

# ==========================================================
# SETTINGS
# ==========================================================

video_path = "VideoFilePath"

# ==========================================================
# OUTPUT
# ==========================================================

output_folder = "Outputs"
os.makedirs(output_folder, exist_ok=True)

video_name = os.path.splitext(os.path.basename(video_path))[0]
csv_name = os.path.join(
    output_folder,
    f"{video_name}_BallCoordinates.csv"
)

# ==========================================================
# VIDEO
# ==========================================================

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError("Could not open video.")

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

annotations = []

clicked_point = None

# ==========================================================
# TRACKER STATE
# ==========================================================

tracker = None
tracker_active = False
ball = None
bbox = None
source = "Hidden"

TRACK_SIZE = 40
frame_number = 0
quit_program = False
go_back = False


# ==========================================================
# MOUSE
# ==========================================================

def mouse(event, x, y, flags, param):
    global clicked_point

    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = (x, y)


cv2.namedWindow("Ball Tracker")
cv2.setMouseCallback(
    "Ball Tracker",
    mouse
)

# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_number += 1

    # ------------------------------------------------------
    # Update tracker
    # ------------------------------------------------------

    if tracker_active:

        success, bbox = tracker.update(frame)

        if success:

            bbox = tuple(map(int, bbox))
            x, y, w, h = bbox

            cx = x + w // 2
            cy = y + h // 2

            ball = (cx, cy)
            source = "Tracker"

        else:

            tracker_active = False
            tracker = None
            ball = None
            bbox = None
            source = "Hidden"

    # ------------------------------------------------------
    # Interaction loop
    # ------------------------------------------------------

    while True:

        display = frame.copy()

        cv2.putText(
            display,
            f"Frame: {frame_number}/{total_frames}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            f"Source: {source}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            "Enter=Accept | Click=Correct | B=Back | N=Hidden | Esc=Quit",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        if bbox is not None:
            x, y, w, h = bbox

            cv2.rectangle(
                display,
                (x, y),
                (x + w, y + h),
                (0, 255, 255),
                2
            )

        if ball is not None:
            cv2.circle(
                display,
                ball,
                6,
                (0, 255, 0),
                -1
            )

        cv2.imshow(
            "Ball Tracker",
            display
        )

        key = cv2.waitKey(20) & 0xFF

        # -----------------------------
        # Mouse click?
        # -----------------------------

        if clicked_point is not None:
            cx, cy = clicked_point

            tracker = cv2.TrackerCSRT_create()

            bbox = (
                cx - TRACK_SIZE // 2,
                cy - TRACK_SIZE // 2,
                TRACK_SIZE,
                TRACK_SIZE
            )

            bbox = tuple(map(int, bbox))

            tracker.init(frame, bbox)

            tracker_active = True
            ball = (cx, cy)
            source = "Manual"

            clicked_point = None
        # -----------------------------
        # Accept frame
        # -----------------------------

        if key == 13:

            if ball is None:

                annotations.append({
                    "Frame": frame_number,
                    "X": np.nan,
                    "Y": np.nan,
                    "Source": "Hidden"
                })

            else:

                annotations.append({
                    "Frame": frame_number,
                    "X": ball[0],
                    "Y": ball[1],
                    "Source": source
                })

            break
        # -----------------------------
        # Hidden
        # -----------------------------

        elif key == ord("n"):

            annotations.append({
                "Frame": frame_number,
                "X": np.nan,
                "Y": np.nan,
                "Source": "Hidden"
            })

            tracker = None
            tracker_active = False
            ball = None
            bbox = None
            source = "Hidden"

            break

        # -----------------------------
        # Go back
        # -----------------------------

        elif key == ord("b"):

            if annotations:
                annotations.pop()

                frame_number -= 2

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    frame_number
                )

                tracker = None
                tracker_active = False
                ball = None
                bbox = None
                source = "Hidden"

                go_back = True

                break

        # -----------------------------
        # Quit
        # -----------------------------

        elif key == 27:

            quit_program = True

            break

    if quit_program:
        break

    if go_back:
        go_back = False
        continue
cap.release()
cv2.destroyAllWindows()

df = pd.DataFrame(annotations)
df.to_csv(csv_name, index=False)

print(f"Saved {len(df)} annotations to:")
print(csv_name)
