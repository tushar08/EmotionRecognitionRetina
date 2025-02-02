import cv2
import os
import json
import numpy as np
from deepface import DeepFace
from retinaface import RetinaFace
from collections import defaultdict

# Configuration
video_path = r"/Users/rahsutikin/Library/Mobile Documents/com~apple~CloudDocs/pers/tusharIdeas/emotionrecognition/AdobeStock_1131581196.mov"
output_folder = "emotion_stats"  # Folder to save JSON files
frame_interval = 25  # Process every 5th frame

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Check if the file exists
if not os.path.exists(video_path):
    print(f"Error: File not found at {video_path}")
    exit()

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video was opened successfully
if not cap.isOpened():
    print(f"Error: Could not open video at {video_path}")
    exit()

# Initialize data structures to track faces and statistics
face_stats = {}  # Dictionary to store statistics for each face
frame_count = 0  # Total frames processed

# Process the video
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Exit the loop if we've reached the end of the video

    frame_count += 1

    # Process only every nth frame
    if frame_count % frame_interval != 0:
        continue

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

                # Initialize face statistics if not already done
                if face_id not in face_stats:
                    face_stats[face_id] = {
                        "total_frames": 0,
                        "emotion_counts": defaultdict(int),
                        "emotion_confidences": defaultdict(list),
                        "embeddings": []
                    }

                # Update face statistics
                face_stats[face_id]["total_frames"] += 1
                face_stats[face_id]["emotion_counts"][dominant_emotion] += 1
                for emotion, score in emotion_scores.items():
                    face_stats[face_id]["emotion_confidences"][emotion].append(score)
                face_stats[face_id]["embeddings"].append(emotion_scores)

                # Draw bounding box and emotion text on the frame (for visualization)
                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                cv2.putText(frame, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error analyzing face: {e}")

    # Display the frame (for debugging)
    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

# Generate and save statistics for each face
for face_id, stats in face_stats.items():
    # Calculate most common emotion
    most_common_emotion = max(stats["emotion_counts"], key=stats["emotion_counts"].get)

    # Calculate average confidence for each emotion
    avg_confidences = {emotion: np.mean(scores) for emotion, scores in stats["emotion_confidences"].items()}

    # Prepare the final statistics dictionary
    face_statistics = {
        "face_id": face_id,
        "total_frames_processed": stats["total_frames"],
        "most_common_emotion": most_common_emotion,
        "emotion_counts": dict(stats["emotion_counts"]),
        "average_confidences": avg_confidences,
        "probabilistic_embeddings_shape": (len(stats["embeddings"]), len(stats["embeddings"][0])),
        "embedding_example": stats["embeddings"][0]  # Example embedding from the first frame
    }

    # Save statistics to a JSON file
    output_file = os.path.join(output_folder, f"face_{face_id}_statistics.json")
    with open(output_file, "w") as f:
        json.dump(face_statistics, f, indent=4)

    print(f"Statistics for face {face_id} saved to {output_file}")

# Save overall statistics
overall_stats = {
    "total_frames_processed": frame_count,
    "total_faces_detected": len(face_stats),
    "faces": list(face_stats.keys())
}

overall_stats_file = os.path.join(output_folder, "overall_statistics.json")
with open(overall_stats_file, "w") as f:
    json.dump(overall_stats, f, indent=4)

print(f"Overall statistics saved to {overall_stats_file}")