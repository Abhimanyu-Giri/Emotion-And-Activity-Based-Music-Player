import cv2
from ultralytics import YOLO
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Path where songs are stored
SONG_DIR = "songs"

# Your YOLO class labels
class_list = ["Driving", "Meditation", "cooking", "reading", "sleeping"]

# Keep track of the currently playing song
current_song = None

import os
import random
import pygame

def play_song_for_class(detected_class):
    global current_song
    folder_name = detected_class.lower()  # Normalize to lowercase
    folder_path = os.path.join(SONG_DIR, folder_name)

    if os.path.exists(folder_path):
        # List all mp3 files in the folder
        mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]

        if mp3_files:
            # Pick a random song
            selected_song = random.choice(mp3_files)
            song_path = os.path.join(folder_path, selected_song)

            if current_song != song_path:
                print(f"Playing song: {selected_song} for class: {detected_class}")
                pygame.mixer.music.stop()
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                current_song = song_path
        else:
            print(f"No .mp3 files found in: {folder_path}")
    else:
        print(f"Folder not found for class '{detected_class}': {folder_path}")

def stop_song():
    pygame.mixer.music.stop()
    print("Song stopped.")

def live_camera_detection():
    model = YOLO("best.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Live detection started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(rgb_frame, imgsz=640, conf=0.4)[0]

        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())

                if cls_id < len(class_list):
                    detected_class = class_list[cls_id]
                    label = f"{detected_class} ({conf*100:.1f}%)"
                    play_song_for_class(detected_class)
                else:
                    label = f"Class {cls_id} ({conf*100:.1f}%)"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, max(30, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2)

        cv2.imshow("Live Detection - YOLOv8", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting detection loop.")
            break

    cap.release()
    cv2.destroyAllWindows()
    stop_song()
