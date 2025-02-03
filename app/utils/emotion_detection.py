import cv2
import os
import json
import base64
import numpy as np
from deepface import DeepFace
from retinaface import RetinaFace
from collections import defaultdict

def process_video(video_path, output_folder, frame_interval=5):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video at {video_path}")

    # Initialize data structures to track faces and statistics
    face_stats = {}
    frame_count = 0

    # Process the video
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Process only every nth frame
        if frame_count % frame_interval != 0:
            continue

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
                            "embeddings": [],
                            "thumbnails": []
                        }

                    # Update face statistics
                    face_stats[face_id]["total_frames"] += 1
                    face_stats[face_id]["emotion_counts"][dominant_emotion] += 1
                    for emotion, score in emotion_scores.items():
                        face_stats[face_id]["emotion_confidences"][emotion].append(score)
                    face_stats[face_id]["embeddings"].append(emotion_scores)

                    # Save the face thumbnail as a base64-encoded image
                    _, buffer = cv2.imencode('.jpg', face_region)
                    face_stats[face_id]["thumbnails"].append(base64.b64encode(buffer).decode('utf-8'))
                except Exception as e:
                    print(f"Error analyzing face: {e}")

    # Release the video capture object
    cap.release()

    # Save statistics for each face
    os.makedirs(output_folder, exist_ok=True)
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
            "embedding_example": stats["embeddings"][0],  # Example embedding from the first frame
            "thumbnails": stats["thumbnails"]  # List of base64-encoded thumbnails
        }

        # Save statistics to a JSON file
        output_file = os.path.join(output_folder, f"face_{face_id}_statistics.json")
        with open(output_file, "w") as f:
            json.dump(face_statistics, f, indent=4)

    # Save overall statistics
    overall_stats = {
        "total_frames_processed": frame_count,
        "total_faces_detected": len(face_stats),
        "faces": list(face_stats.keys())
    }

    overall_stats_file = os.path.join(output_folder, "overall_statistics.json")
    with open(overall_stats_file, "w") as f:
        json.dump(overall_stats, f, indent=4)