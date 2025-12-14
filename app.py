from flask import Flask, render_template, flash, redirect, url_for, session, request,jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, redirect, url_for, render_template, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import subprocess

from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from deepface import DeepFace
import cv2
# from index import d_dtcn

import os
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            message = 'Logged in successfully !'
            return render_template('base.html', message=message)
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('register.html')

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route("/home", methods=['GET', 'POST'])
def home():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Continue') == 'Continue':
            return render_template("test1.html")
    else:
        return render_template("base.html")
    
@app.route("/start", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('Start') == 'Start':
            # Run detect.py as a separate process
            subprocess.Popen(['python', 'detect2.py'])
            return render_template("base.html")
    return render_template("base.html")



@app.route("/hello", methods=['GET', 'POST'])
def amol():
    if request.method == 'POST':
        if request.form.get('hello') == 'hello':
            try:
                script_path = os.path.join(os.getcwd(), 'infer_camera.py')
                subprocess.Popen(['python', script_path])  # Or use 'pythonw' on Windows
                return render_template("base.html", message="Script started successfully.")
            except Exception as e:
                return render_template("base.html", message=f"Error: {e}")
    return render_template("base.html", message=None)


# @app.route('/activity')
# def activity():
# 	return render_template("upload.html")



@app.route('/test')
def test():
	return render_template("test1.html")



@app.route('/contact', methods=['GET', 'POST'])
def cool_form():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))
    # show the form, it wasn't submitted
    return render_template('contact.html')


def get_song_list(time_period):
    folder = f"static/{'day_song' if time_period == 'Day' else 'night_song'}"
    return [f for f in os.listdir(folder) if f.endswith(".mp3")]

# API to get songs based on selection
@app.route("/get_songs")
def get_songs():
    time_period = request.args.get("time_period")
    songs = get_song_list(time_period) if time_period else []
    return jsonify({"songs": songs})

@app.route("/song")
@app.route("/song")
def song():
    return render_template("song.html")

@app.route("/predict", methods=["POST"])
def predict():
    time_period = request.form.get("time_period")
    song_name = request.form.get("song")  # Get selected song from form

    return render_template("predict.html", time_period=time_period, song=song_name)




from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from process_video import process_video



# Define folders
UPLOAD_FOLDER = "static/uploads/"
PROCESSED_FOLDER = "static/processed/"
Driving_FOLDER = "static/songs/Driving/"
Meditation_FOLDER = "static/songs/Meditation/"
cooking_FOLDER = "static/songs/cooking/"
reading_FOLDER = "static/songs/reading/"
sleeping_FOLDER = "static/songs/sleeping/"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER
app.config["Driving_FOLDER"] = Driving_FOLDER
app.config["Meditation_FOLDER"] = Meditation_FOLDER
app.config["cooking_FOLDER"] = cooking_FOLDER
app.config["reading_FOLDER"] = reading_FOLDER
app.config["sleeping_FOLDER"] = sleeping_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(Driving_FOLDER, exist_ok=True)
os.makedirs(Meditation_FOLDER, exist_ok=True)
os.makedirs(cooking_FOLDER, exist_ok=True)
os.makedirs(reading_FOLDER, exist_ok=True)
os.makedirs(sleeping_FOLDER, exist_ok=True)

# Song recommendations (running -> day songs, sleeping -> night songs)
song_recommendations = {
    "Driving": Driving_FOLDER,
    "Meditation": Meditation_FOLDER,
    "cooking": cooking_FOLDER,
    "reading": reading_FOLDER,
    "sleeping": sleeping_FOLDER,
    
}

@app.route('/activity')
def activity():
    return render_template("upload.html")




@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "video" not in request.files:
            return render_template("upload.html", error="No file uploaded")

        file = request.files["video"]
        if file.filename == "":
            return render_template("upload.html", error="No selected file")

        if file:
            filename = secure_filename(file.filename)
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(video_path)

            # Process video
            output_video, detected_objects = process_video(video_path, app.config["PROCESSED_FOLDER"])

            if not output_video:
                return render_template("upload.html", error="Error processing video")

            # Get recommended songs based on detected objects
            recommended_songs = {}
            for obj in detected_objects.keys():
                if obj in song_recommendations:
                    song_folder = song_recommendations[obj] + "/"
                    song_list = [
                        os.path.join(song_folder, song) for song in os.listdir(song_folder) if song.endswith(".mp3")
                    ]
                    recommended_songs[obj] = song_list

            return render_template("result.html",
                                   uploaded_video=video_path,  # Pass original video
                                   processed_video=output_video,  # Pass processed video
                                   detected_objects=detected_objects.keys(),
                                   recommended_songs=recommended_songs)

    return render_template("upload.html")

from live_camera_detection import live_camera_detection, stop_song
import threading

@app.route('/shubham')
def shubham():
    return render_template('live_detection.html')


@app.route('/start_camera')
def start_camera():
    # Run detection in a separate thread to avoid blocking
    threading.Thread(target=live_camera_detection).start()
    return "Camera started. Check the OpenCV window. Press 'q' to stop."



@app.route('/stop_song')
def stop_song_route():
    stop_song()
    return "Song stopped."
 




from mood_analysis import get_mood, is_gym_related
from youtube_recommender import get_youtube_url



def extract_video_id(url):
    return url.split("v=")[-1].split("&")[0]


@app.route("/pradip")
def pradip():
    return render_template("text.html")




@app.route("/get_song", methods=["POST"])
def get_song():
    data = request.json
    text = data.get("text", "")
    
    
    if is_gym_related(text):
        mood = "gym"
    else:
        mood = get_mood(text)
    url = get_youtube_url(mood)
    video_id = extract_video_id(url)
    return jsonify({"mood": mood, "video_id": video_id})




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, use_reloader=False)
