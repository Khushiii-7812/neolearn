import cv2
import face_recognition
import numpy as np
import os
import pickle
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# Load all embeddings
known_encodings = []
known_names = []

for file in os.listdir('data/embeddings'):
    if file.endswith('.pkl'):
        name = file.replace('.pkl', '')
        with open(f'data/embeddings/{file}', 'rb') as f:
            embeddings = pickle.load(f)
            known_encodings.extend(embeddings)
            known_names.extend([name] * len(embeddings))

print(f"[INFO] Loaded {len(known_encodings)} face encodings.")

# Attendance tracking
attended_today = set()
COL_NAMES = ['NAME', 'TIME']

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding, box in zip(encodings, boxes):
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
        name = "Unknown"

        if True in matches:
            matched_idxs = [i for i, m in enumerate(matches) if m]
            name_counts = {}
            for i in matched_idxs:
                name_counts[known_names[i]] = name_counts.get(known_names[i], 0) + 1
            name = max(name_counts, key=name_counts.get)

        # Draw result
        top, right, bottom, left = box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, top - 40), (right, top), (0, 255, 0), -1)
        cv2.putText(frame, name, (left + 5, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Save attendance
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        attendance_file = f"Attendance/Attendance_{date}.csv"
        exist = os.path.isfile(attendance_file)

        if name != "Unknown" and name not in attended_today:
            attended_today.add(name)
            speak(f"Attendance marked for {name}")
            with open(attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not exist:
                    writer.writerow(COL_NAMES)
                writer.writerow([name, timestamp])
            time.sleep(2)

    cv2.imshow("Face Attendance", frame)
    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
