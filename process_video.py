import cv2
from ultralytics import YOLO
import os

# Define activity-based song recommendations
activity_songs = {
    "Driving": ["Highway to Hell - AC/DC", "Life is a Highway - Rascal Flatts", "Drive - Incubus"],
    "Meditation": ["Weightless - Marconi Union", "Relaxing Flute Music", "Om Chanting"],
    "cooking": ["Sugar - Maroon 5", "Cake by the Ocean - DNCE", "Banana Pancakes - Jack Johnson"],
    "reading": ["Clair de Lune - Debussy", "Lo-fi Study Beats", "Beethoven - Moonlight Sonata"],
    "sleeping": ["Calm Rain Sounds", "Soft Piano Music", "Deep Sleep Delta Waves"]
}

def process_video(video_path, output_folder):
    model = YOLO("best.pt")  # Load trained YOLO model
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Video could not be opened.")
        return None, {}, {}

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    output_path = os.path.join(output_folder, os.path.basename(video_path))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    unique_objects = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]  # Get the first result only (per frame)

        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cls = int(box.cls.item())
                conf = round(float(box.conf.item()), 2)

                # List of custom classes - update based on your training
                class_list = ["Driving", "Meditation", "cooking", "reading", "sleeping"]
                object_name = class_list[cls] if cls < len(class_list) else f"Class {cls}"

                if object_name not in unique_objects:
                    unique_objects[object_name] = conf

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.putText(frame, f"{object_name} ({conf*100:.1f}%)", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        out.write(frame)

    cap.release()
    out.release()

    # Song recommendation based on detected activities
    recommended_songs = {
        activity: activity_songs.get(activity, ["No recommendation found"])
        for activity in unique_objects
    }

    return output_path, unique_objects
