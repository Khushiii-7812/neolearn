import cv2
import face_recognition
import pickle
import os

if not os.path.exists('data/embeddings'):
    os.makedirs('data/embeddings')

video = cv2.VideoCapture(0)

name = input("Enter Your Name: ").strip()
embeddings = []
count = 0

while True:
    ret, frame = video.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)

    for box in boxes:
        encodings = face_recognition.face_encodings(rgb, [box])
        if encodings:
            embeddings.append(encodings[0])
            count += 1

        cv2.rectangle(frame, (box[3], box[0]), (box[1], box[2]), (0, 255, 0), 2)
        cv2.putText(frame, str(count), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Capturing Faces", frame)
    if cv2.waitKey(1) == ord('q') or count >= 20:
        break

video.release()
cv2.destroyAllWindows()

# Save embeddings
with open(f'data/embeddings/{name}.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

print(f"[INFO] Saved {count} embeddings for {name}")
