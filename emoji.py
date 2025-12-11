import cv2
import tkinter as tk
from PIL import Image, ImageTk
import pygame
import random
import time

# Emotion to emoji mapping
emotion_to_emoji = {
    "happy": "😄",
    "sad": "😢",
    "angry": "😡",
    "surprise": "😲",
    "neutral": "😐",
    "fear": "😨",
    "disgust": "🤢"
}

# Emotion to music mapping - Each emotion gets its specific song
emotion_to_songs = {
    "happy": ["songs/songshappy1.mp3"],
    "sad": ["songs/songssad1.mp3"],
    "angry": ["songs/songsangry1.mp3"],
    "surprise": ["songs/songssurprise1.mp3"],
    "neutral": ["songs/songsneutral1.mp3"],
    "fear": ["songs/songsfear1.mp3"],
    "disgust": ["songs/songsdisgust1.mp3"]
}

# All available songs for variety
all_songs = [
    "songs/songshappy1.mp3",
    "songs/songssad1.mp3", 
    "songs/songsangry1.mp3",
    "songs/songssurprise1.mp3",
    "songs/songsneutral1.mp3",
    "songs/songsfear1.mp3",
    "songs/songsdisgust1.mp3"
]

# Init pygame for music
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)  # Set volume to maximum (0.0 to 1.0)

# Load face detection cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Camera setup
cap = cv2.VideoCapture(0)

# GUI setup
root = tk.Tk()
root.title("Emotion Music Player")
root.geometry("800x600")

video_label = tk.Label(root)
video_label.pack()

emoji_label = tk.Label(root, text="🙂", font=("Arial", 50))
emoji_label.pack()

status_label = tk.Label(root, text="Detecting emotion...", font=("Arial", 14))
status_label.pack()

current_song = None
last_emotion_change = time.time()
current_emotion = "neutral"
last_played_song = None

def play_song(emotion):
    global current_song, last_played_song
    
    print(f"DEBUG: play_song called with emotion: {emotion}")
    
    # First try to play the emotion-specific song
    song_list = emotion_to_songs.get(emotion, [])
    print(f"DEBUG: Found song list for {emotion}: {song_list}")
    
    if song_list:
        preferred_song = song_list[0]
        print(f"DEBUG: Preferred song: {preferred_song}")
        print(f"DEBUG: Last played song: {last_played_song}")
        
        # If this is a different emotion, play its specific song
        if preferred_song != last_played_song:
            song = preferred_song
        else:
            # If same emotion, pick a random different song from all available
            available_songs = [s for s in all_songs if s != last_played_song]
            song = random.choice(available_songs) if available_songs else preferred_song
        
        print(f"DEBUG: Selected song to play: {song}")
        
        try:
            # Check if file exists
            import os
            if os.path.exists(song):
                print(f"DEBUG: File exists: {song}")
            else:
                print(f"DEBUG: File NOT found: {song}")
                return
                
            # Stop current music and play new song
            pygame.mixer.music.stop()
            print(f"DEBUG: Loading song: {song}")
            pygame.mixer.music.load(song)
            print(f"DEBUG: Playing song...")
            pygame.mixer.music.play()
            current_song = song
            last_played_song = song
            song_name = song.split('/')[-1].replace('songs', '').replace('.mp3', '')
            status_label.config(text=f"Playing: {emotion} - {song_name}")
            print(f"DEBUG: Successfully started playing {emotion} - {song}")
            print(f"DEBUG: Music playing status: {pygame.mixer.music.get_busy()}")
            print(f"DEBUG: Current volume: {pygame.mixer.music.get_volume()}")  # Debug output
        except Exception as e:
            status_label.config(text=f"Error playing: {song}")
            print(f"DEBUG: Error playing {song}: {e}")  # Debug output
    else:
        print(f"DEBUG: No songs found for emotion: {emotion}")

def stop_song():
    pygame.mixer.music.stop()
    status_label.config(text="Stopped")

def pause_song():
    pygame.mixer.music.pause()
    status_label.config(text="Paused")

def resume_song():
    pygame.mixer.music.unpause()
    status_label.config(text=f"Playing: {current_song}")

def detect_emotion_simple(frame):
    """Simple emotion detection based on face detection and basic heuristics"""
    global current_emotion, last_emotion_change
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # Face detected - simulate emotion changes
        current_time = time.time()
        if current_time - last_emotion_change > 5:  # Change emotion every 5 seconds
            # Only select non-neutral emotions for active detection
            emotions = [e for e in emotion_to_emoji.keys() if e != "neutral"]
            # Make sure we don't pick the same emotion twice in a row
            available_emotions = [e for e in emotions if e != current_emotion]
            if available_emotions:
                new_emotion = random.choice(available_emotions)
                print(f"DEBUG: Face detected, changing from {current_emotion} to {new_emotion}")
                current_emotion = new_emotion
            else:
                current_emotion = random.choice(emotions)
            last_emotion_change = current_time
    else:
        # No face detected - show neutral but don't change current_emotion for comparison
        if current_emotion != "neutral":
            print(f"DEBUG: No face detected, showing neutral")
        return "neutral"
    
    return current_emotion

def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert image to RGB for Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        # Detect emotion
        try:
            emotion = detect_emotion_simple(frame)
            emoji_label.config(text=emotion_to_emoji.get(emotion, "❓"))
            # Only play song when emotion changes (not for neutral or repeated emotions)
            if emotion != "neutral":
                print(f"DEBUG: Current emotion: {emotion}, Previous: {getattr(update_frame, 'prev_emotion', 'none')}")
                if not hasattr(update_frame, 'prev_emotion') or emotion != update_frame.prev_emotion:
                    print(f"DEBUG: Emotion changed to {emotion}, playing song")
                    play_song(emotion)
                    update_frame.prev_emotion = emotion
        except Exception as e:
            # If emotion detection fails, keep the current emoji
            print(f"DEBUG: Emotion detection error: {e}")
            pass

    root.after(1000, update_frame)  # refresh every second

def change_emotion_manually():
    global current_emotion, last_emotion_change
    # Only select non-neutral emotions for manual changes
    emotions = [e for e in emotion_to_emoji.keys() if e != "neutral"]
    # Pick a random emotion different from current
    available_emotions = [e for e in emotions if e != current_emotion]
    if available_emotions:
        current_emotion = random.choice(available_emotions)
    else:
        current_emotion = random.choice(emotions)
    last_emotion_change = time.time()
    print(f"DEBUG: Manual emotion change to {current_emotion}")  # Debug output
    # Force play the new emotion's song
    play_song(current_emotion)
    # Update emoji immediately
    emoji_label.config(text=emotion_to_emoji.get(current_emotion, "❓"))

def play_random_song():
    global current_song, last_played_song
    # Pick a random song different from the last one
    available_songs = [s for s in all_songs if s != last_played_song]
    if available_songs:
        song = random.choice(available_songs)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()
            current_song = song
            last_played_song = song
            song_name = song.split('/')[-1].replace('songs', '').replace('.mp3', '')
            status_label.config(text=f"Playing random: {song_name}")
            print(f"DEBUG: Playing random song - {song}")
        except Exception as e:
            status_label.config(text=f"Error playing: {song}")
            print(f"DEBUG: Error playing {song}: {e}")

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Stop", command=stop_song, width=10).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Pause", command=pause_song, width=10).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Resume", command=resume_song, width=10).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Change Emotion", command=change_emotion_manually, width=12).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="Random Song", command=play_random_song, width=12).grid(row=0, column=4, padx=5)
tk.Button(btn_frame, text="Exit", command=lambda: (cap.release(), root.destroy()), width=10).grid(row=0, column=5, padx=5)

update_frame()
root.mainloop()