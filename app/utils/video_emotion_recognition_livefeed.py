import cv2
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import numpy as np
import time
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the model and processor
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "motheecreator/vit-Facial-Expression-Recognition"
model = AutoModelForImageClassification.from_pretrained(model_name).to(device)
processor = AutoImageProcessor.from_pretrained(model_name)

# Initialize face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Function to preprocess frames and predict emotions
def predict_emotion_from_frame(frame):
    try:
        # Convert OpenCV frame (BGR) to PIL image (RGB)
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Preprocess the image
        inputs = processor(images=pil_image, return_tensors="pt").to(device)
        # Predict
        with torch.no_grad():
            outputs = model(**inputs)
        # Softmax probabilities
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        predicted_class = probs.argmax().item()
        confidence = probs[predicted_class].item()
        label = model.config.id2label[predicted_class]
        return label, confidence, probs.cpu().numpy()  # Return probabilities
    except Exception as e:
        return f"Error: {e}", 0, np.zeros(len(model.config.id2label))

# OpenCV video capture
cap = cv2.VideoCapture(0)  # 0 is the default camera. Change for external cameras.

# Parameters
duration = 60  # in seconds
start_time = time.time()

# Data collection
emotion_data = []
embedding_data = []

# Set up matplotlib real-time chart
plt.ion()
fig, ax = plt.subplots()
labels = list(model.config.id2label.values())
emotion_counts = {label: 0 for label in labels}
bars = ax.bar(emotion_counts.keys(), emotion_counts.values())
ax.set_title("Real-Time Emotion Distribution")
ax.set_ylabel("Count")

def update_chart():
    for bar, label in zip(bars, labels):
        bar.set_height(emotion_counts[label])
    plt.pause(0.01)

print("Running video feed for 1 minute. Press 'q' to quit early.")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect faces
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    
    for (x, y, w, h) in faces:
        # Crop the face
        face_frame = frame[y:y+h, x:x+w]
        emotion, confidence, probabilities = predict_emotion_from_frame(face_frame)
        
        # Record data
        emotion_data.append((emotion, confidence))
        embedding_data.append(probabilities)  # Probabilistic facial embeddings
        emotion_counts[emotion] += 1
        
        # Display emotion on video
        cv2.putText(frame, f"{emotion} ({confidence * 100:.1f}%)", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    # Show the video frame
    cv2.imshow("Facial Emotion Recognition", frame)
    
    # Update real-time chart
    update_chart()
    
    # Break if 'q' is pressed or time exceeds 1 minute
    if cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time > duration:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Generate statistics
if emotion_data:
    # Extract emotions and confidences
    emotions = [e[0] for e in emotion_data]
    confidences = [e[1] for e in emotion_data]
    
    # Most common emotion
    most_common_emotion = Counter(emotions).most_common(1)[0]
    
    # Average confidence
    avg_confidence = np.mean(confidences)
    
    # Probabilistic embedding as a numpy array
    embedding_data = np.array(embedding_data)
    
    print("\nStatistics:")
    print(f"Most Common Emotion: {most_common_emotion[0]} ({most_common_emotion[1]} times)")
    print(f"Average Confidence: {avg_confidence * 100:.2f}%")
    print(f"Total Frames Processed: {len(emotion_data)}")
    
    print("\nProbabilistic Embeddings Shape:", embedding_data.shape)
    print("Embedding Example (First Frame):", embedding_data[0])
else:
    print("No data collected. Check the video feed or camera settings.")

# Save embeddings and statistics for further analysis
np.save("emotion_embeddings.npy", embedding_data)
with open("emotion_statistics.txt", "w") as f:
    f.write(f"Most Common Emotion: {most_common_emotion[0]} ({most_common_emotion[1]} times)\n")
    f.write(f"Average Confidence: {avg_confidence * 100:.2f}%\n")
    f.write(f"Total Frames Processed: {len(emotion_data)}\n")
