
import cv2
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import pygame
import time
from datetime import datetime
import os
import numpy as np
from flask import Flask, Response, render_template_string
import threading
import sys

# Initialize Flask app
app = Flask(__name__)

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
    print("Pygame mixer initialized successfully")
except pygame.error as e:
    print(f"Failed to initialize pygame mixer: {e}")

# Set device to CPU
device = torch.device("cpu")

# Load model with weights parameter (using IMAGENET1K_V1 weights)
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)  # 5 classes
try:
    model.load_state_dict(torch.load("activity_detection_model.pth"))
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
model = model.to(device)
model.eval()

# Class names (must match training dataset)
class_names = ['Driving', 'Meditation', 'cooking', 'reading', 'sleeping']

# Base directory for songs
songs_base_dir = os.path.join(os.getcwd(), "songs")

# Initialize song recommendations
song_recommendations = {
    'Driving': [],
    'Meditation': [],
    'cooking': [],
    'reading': [],
    'sleeping': []
}

# Scan subfolders for MP3 files
missing_folders = []
for activity in song_recommendations:
    activity_dir = os.path.join(songs_base_dir, activity)
    if not os.path.exists(activity_dir):
        missing_folders.append(activity_dir)
        continue
    mp3_files = [f for f in os.listdir(activity_dir) if f.lower().endswith('.mp3')]
    if not mp3_files:
        print(f"Warning: No MP3 files found in {activity_dir}")
    for mp3_file in mp3_files:
        song_recommendations[activity].append({
            'title': mp3_file,
            'file': mp3_file
        })

if missing_folders:
    print("Warning: The following activity folders are missing:")
    for folder in missing_folders:
        print(f" - {folder}")
    print("Please create these folders and add MP3 files.")
print("Song recommendations:", song_recommendations)

# Transform for camera input
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Initialize webcam
def initialize_webcam(index=0, backend=cv2.CAP_ANY):
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap

camera_indices = [0, 1, 2]
backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW, cv2.CAP_ANY]
cap = None

for backend in backends:
    for index in camera_indices:
        print(f"Trying camera index {index} with backend {backend}...")
        cap = initialize_webcam(index, backend)
        if cap is not None:
            print(f"Successfully opened camera index {index} with backend {backend}")
            break
    if cap is not None:
        break

if cap is None:
    print("Error: Could not open any webcam. Please check your camera and drivers.")
    sys.exit(1)

# Global variables
last_activity = None
last_song = None
last_log_time = 0
log_interval = 5
song_selection_mode = False
song_selection_start = 0
song_selection_timeout = 10  # Increased timeout
selected_songs = {}
song_playing = False
confidence_threshold = 0.5  # Lowered threshold
activity_log = open("activity.txt", "a")
current_frame = None
current_activity = "Unknown"
current_confidence = 0.0

# Lock for thread safety
lock = threading.Lock()

def play_song_file(activity, song_index):
    global song_playing
    songs = song_recommendations.get(activity, [])
    if not songs:
        print(f"No songs available for {activity}")
        return
    song_file = os.path.join(songs_base_dir, activity, songs[song_index]['file'])
    print(f"Attempting to play: {song_file}")
    if not os.path.exists(song_file):
        print(f"Error: File does not exist: {song_file}")
        return
    try:
        print(f"Stopping current music...")
        pygame.mixer.music.stop()
        print(f"Loading song: {song_file}")
        pygame.mixer.music.load(song_file)
        print(f"Playing song: {song_file}")
        pygame.mixer.music.play()
        song_playing = True
        print(f"Successfully playing: {songs[song_index]['title']}")
    except pygame.error as e:
        print(f"Error playing song for {activity}: {e}")
        song_playing = False

def generate_frames():
    global current_frame, current_activity, current_confidence
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Retrying...")
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            # Preprocess frame for prediction
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            input_tensor = transform(pil_image).unsqueeze(0).to(device)

            # Predict activity
            with torch.no_grad():
                outputs = model(input_tensor)
                probs = torch.softmax(outputs, dim=1)
                confidence, pred = torch.max(probs, 1)
                confidence_score = confidence.item()
                print("Probabilities:", {class_names[i]: probs[0][i].item() for i in range(len(class_names))})
                if confidence_score >= confidence_threshold:
                    predicted_class = class_names[pred.item()]
                else:
                    predicted_class = "Unknown"

            # Update global variables
            with lock:
                current_activity = predicted_class
                current_confidence = confidence_score

            # Log activity
            current_time = time.time()
            global last_activity, last_log_time, last_song, song_selection_mode, song_selection_start, selected_songs, song_playing
            if predicted_class != "Unknown" and (predicted_class != last_activity or (current_time - last_log_time) >= log_interval):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"{timestamp} - Activity: {predicted_class} (Confidence: {confidence_score:.2f})\n"
                activity_log.write(log_entry)
                activity_log.flush()
                last_activity = predicted_class
                last_log_time = current_time

            # Handle song selection
            if predicted_class in song_recommendations and predicted_class != last_song:
                songs = song_recommendations[predicted_class]
                if songs:
                    song_selection_mode = True
                    song_selection_start = current_time
                    last_song = predicted_class
                    if predicted_class not in selected_songs:
                        selected_songs[predicted_class] = 0

            # Timeout for song selection (auto-play default song)
            if song_selection_mode and (current_time - song_selection_start) >= song_selection_timeout:
                song_selection_mode = False
                songs = song_recommendations.get(predicted_class, [])
                if songs:
                    play_song_file(predicted_class, selected_songs.get(predicted_class, 0))

            # Overlay activity label in orange at top-left
            activity_text = f"{predicted_class}"
            cv2.putText(frame, activity_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

        # Encode frame for streaming
        with lock:
            current_frame = frame.copy()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Activity Detection</title>
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #000000;
                font-family: Arial, sans-serif;
                color: white;
            }
            img {
                border: 2px solid #333;
            }
            .button-container {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 10px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #555;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #777;
            }
        </style>
    </head>
    <body>
        <h1>Activity Detection</h1>
        <img src="{{ url_for('video_feed') }}" width="640" height="480">
        <div class="button-container">
            <form action="/play" method="post">
                <button type="submit">Play!</button>
            </form>
            <form action="/stop" method="post">
                <button type="submit">Stop</button>
            </form>
            <form action="/change" method="post">
                <button type="submit">Change Song</button>
            </form>
            <form action="/exit" method="post">
                <button type="submit">Exit</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play', methods=['POST'])
def play_song():
    global song_playing, song_selection_mode, song_selection_start
    with lock:
        if current_activity in song_recommendations and current_activity in selected_songs:
            play_song_file(current_activity, selected_songs[current_activity])
        else:
            song_selection_mode = True
            song_selection_start = time.time()
            print("No song selected. Select a song.")
    return '', 204

@app.route('/stop', methods=['POST'])
def stop_song():
    global song_playing, song_selection_mode, last_song
    pygame.mixer.music.stop()
    song_playing = False
    song_selection_mode = False
    last_song = None  # Allow replay on next detection
    print("Song stopped.")
    return '', 204

@app.route('/change', methods=['POST'])
def change_song():
    global song_selection_mode, song_selection_start, selected_songs, song_playing
    with lock:
        if current_activity in song_recommendations:
            songs = song_recommendations[current_activity]
            if songs:
                next_index = (selected_songs.get(current_activity, 0) + 1) % len(songs)
                selected_songs[current_activity] = next_index
                play_song_file(current_activity, next_index)
                song_selection_mode = True
                song_selection_start = time.time()
                print(f"Change song for {current_activity}. Select a new song via console if desired.")
            else:
                print(f"No songs available for {current_activity}.")
        else:
            print(f"No songs available for {current_activity}.")
    return '', 204

@app.route('/exit', methods=['POST'])
def exit_app():
    global cap, activity_log
    pygame.mixer.music.stop()
    if cap is not None:
        cap.release()
    if activity_log:
        activity_log.close()
    print("Exiting application...")
    os._exit(0)
    return '', 204

def select_song():
    """Thread to handle song selection based on user input in the console."""
    global song_selection_mode, song_selection_start, selected_songs, song_playing
    while True:
        print("Song selection thread running...")
        if song_selection_mode:
            current_time = time.time()
            if current_time - song_selection_start < song_selection_timeout:
                songs = song_recommendations.get(current_activity, [])
                if songs:
                    print("\nAvailable songs for", current_activity, ":")
                    for i, song in enumerate(songs):
                        print(f"{i+1}: {song['title']}")
                    choice = input(f"Select a song (1-{len(songs)}) or press Enter to skip: ")
                    if choice.strip() == "":
                        print("Skipped console selection.")
                        song_selection_mode = False
                        continue
                    try:
                        choice = int(choice) - 1
                        if 0 <= choice < len(songs):
                            with lock:
                                selected_songs[current_activity] = choice
                                song_selection_mode = False
                                play_song_file(current_activity, choice)
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            else:
                song_selection_mode = False
                print("Song selection timed out.")
        time.sleep(0.1)

if __name__ == '__main__':
    song_selection_thread = threading.Thread(target=select_song, daemon=True)
    song_selection_thread.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)