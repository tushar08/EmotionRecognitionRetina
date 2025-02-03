from flask import Flask, render_template, request, jsonify, Response
import os
import base64
import cv2
import json
from utils.emotion_detection import process_video
from utils.generative_ai import train_generative_model, generate_synthetic_image
from huggingface_hub import login

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATS_FOLDER'] = 'emotion_stats'
app.config['GENAI_FOLDER'] = 'generative_ai_data'

# Ensure upload, stats, and generative AI folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATS_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENAI_FOLDER'], exist_ok=True)

# Hugging Face credentials (loaded from environment variables)
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_huggingface', methods=['POST'])
def login_huggingface():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "No token provided"}), 400

    try:
        # Log in to Hugging Face
        login(token=token)
        return jsonify({"message": "Logged in to Hugging Face successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded video
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
    video_file.save(video_path)

    # Get frame interval from the UI
    frame_interval = int(request.form.get('frame_interval', 5))

    # Process the video and persist frame data
    stats_folder = os.path.join(app.config['STATS_FOLDER'], os.path.splitext(video_file.filename)[0])
    os.makedirs(stats_folder, exist_ok=True)
    process_video(video_path, stats_folder, frame_interval)

    return jsonify({"message": "Video processed successfully", "stats_folder": stats_folder})

@app.route('/record_video', methods=['POST'])
def record_video():
    # Capture video from webcam
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'webcam_video.mp4')
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    # Record for 10 seconds (adjust as needed)
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < 10:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    # Process the recorded video
    stats_folder = os.path.join(app.config['STATS_FOLDER'], 'webcam_video')
    os.makedirs(stats_folder, exist_ok=True)
    process_video(video_path, stats_folder, frame_interval=5)

    return jsonify({"message": "Video recorded and processed successfully", "stats_folder": stats_folder})

@app.route('/video_feed')
def video_feed():
    video_path = request.args.get('video_path')
    frame_interval = int(request.args.get('frame_interval', 5))

    def generate_frames():
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval != 0:
                continue

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cap.release()

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame', methods=['POST'])
def save_frame():
    frame_data = request.json.get('frame_data')
    frame_path = os.path.join(app.config['GENAI_FOLDER'], 'saved_frame.jpg')

    with open(frame_path, 'wb') as f:
        f.write(frame_data)

    return jsonify({"message": "Frame saved successfully", "frame_path": frame_path})

@app.route('/train_generative_model', methods=['POST'])
def train_model():
    try:
        # Train the generative AI model using saved frames
        model_path = train_generative_model(app.config['GENAI_FOLDER'])
        return jsonify({"message": "Generative model trained successfully", "model_path": model_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_synthetic_image', methods=['POST'])
def generate_image():
    try:
        # Get the model name from the request
        model_name = request.json.get('model_name', 'stabilityai/stable-diffusion-2')
        prompt = request.json.get('prompt', 'A realistic face showing happiness')

        # Generate a synthetic image using the specified model
        output_path = generate_synthetic_image(prompt, model_name)
        return jsonify({"message": "Synthetic image generated successfully", "output_path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)