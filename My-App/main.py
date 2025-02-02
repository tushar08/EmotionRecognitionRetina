import cv2
import numpy as np
from deepface import DeepFace
from retinaface import RetinaFace

# Open the video file
video_path = '/Users/rahsutikin/Library/"Mobile Documents"/com~apple~CloudDocs/pers/tusharIdeas/emotionrecognition/AdobeStock_1131581196.mov'
# 'path_to_your_video.mp4'  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# Check if the video was opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Dictionary to store emotion statistics
emotion_stats = {}

# Process each frame in the video
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Exit the loop if we've reached the end of the video

    frame_count += 1
    print(f"Processing frame {frame_count}...")

    # Detect faces using RetinaFace
    faces = RetinaFace.detect_faces(frame)

    if isinstance(faces, dict):  # Check if faces are detected
        for face_id, face_data in faces.items():
            # Extract face bounding box
            x, y, w, h = face_data['facial_area']
            x, y, w, h = int(x), int(y), int(w), int(h)

            # Extract the face region
            face_region = frame[y:h, x:w]

            # Analyze emotions using DeepFace
            try:
                emotion_analysis = DeepFace.analyze(face_region, actions=['emotion'], enforce_detection=False)
                dominant_emotion = emotion_analysis[0]['dominant_emotion']
                emotion_scores = emotion_analysis[0]['emotion']

                # Update emotion statistics
                for emotion, score in emotion_scores.items():
                    if emotion in emotion_stats:
                        emotion_stats[emotion].append(score)
                    else:
                        emotion_stats[emotion] = [score]

                # Draw bounding box and emotion text on the frame
                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                cv2.putText(frame, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error analyzing face: {e}")

    # Display the frame
    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

# Calculate and print the average emotion statistics
print("\nEmotion Statistics:")
for emotion, scores in emotion_stats.items():
    avg_score = np.mean(scores)
    print(f"{emotion}: {avg_score:.2f}")