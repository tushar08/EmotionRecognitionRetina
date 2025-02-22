from flask import Flask, render_template, request, jsonify, Response
import os
import base64
import json
import cv2
from utils.emotion_detection import process_video
from utils.generative_ai import train_generative_model, generate_synthetic_image_with_ip
from huggingface_hub import login
from transformers import pipeline  # Import Hugging Face pipeline for text generation
import logging

logging.basicConfig(level=logging.DEBUG)

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

# Load a text generation model from Hugging Face
story_generator = pipeline("text-generation", model="gpt2")  # You can replace "gpt2" with any other model

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_huggingface', methods=['POST'])
def login_huggingface():
    logging.debug("Route hit: /login_huggingface")
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "No token provided"}), 400

    try:
        login(token=token)
        return jsonify({"message": "Logged in to Hugging Face successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_video():
    logging.debug("Route hit: /upload")
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
    video_file.save(video_path)

    frame_interval = int(request.form.get('frame_interval', 40))

    stats_folder = os.path.join(app.config['STATS_FOLDER'], os.path.splitext(video_file.filename)[0])
    os.makedirs(stats_folder, exist_ok=True)
    process_video(video_path, stats_folder, frame_interval)

    return jsonify({"message": "Video processed successfully", "stats_folder": stats_folder})

@app.route('/video_feed')
def video_feed():
    logging.debug("Route hit: /video_feed")
    video_path = request.args.get('video_path')
    frame_interval = int(request.args.get('frame_interval', 40))

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

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cap.release()

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame', methods=['POST'])
def save_frame():
    logging.debug("Route hit: /save_frame")
    frame_data = request.json.get('frame_data')
    logging.debug(f"Received frame data: {frame_data[:100]}...")
    if not frame_data:
        return jsonify({"error": "No frame data provided"}), 400

    try:
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_path = os.path.join(app.config['GENAI_FOLDER'], 'saved_frame.jpg')
        with open(frame_path, 'wb') as f:
            f.write(frame_bytes)

        return jsonify({"message": "Frame saved successfully", "frame_path": frame_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_stats', methods=['GET'])
def get_stats():
    logging.debug("Route hit: /get_stats")
    stats_folder = request.args.get('stats_folder')
    if not stats_folder or not os.path.exists(stats_folder):
        return jsonify({"error": "Statistics folder not found"}), 404

    try:
        stats_files = [f for f in os.listdir(stats_folder) if f.endswith('.json')]
        stats = {}
        for stats_file in stats_files:
            with open(os.path.join(stats_folder, stats_file), 'r') as f:
                stats[stats_file] = json.load(f)

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/train_generative_model', methods=['POST'])
def train_model():
    logging.debug("Route hit: /train_generative_model")
    try:
        model_path = train_generative_model(app.config['GENAI_FOLDER'])
        return jsonify({"message": "Generative model trained successfully", "model_path": model_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_synthetic_image', methods=['POST'])
def generate_image():
    logging.debug("Route hit: /generate_synthetic_image")
    try:
        model_name = request.json.get('model_name')
        prompt = request.json.get('prompt')

        if not model_name:
            return jsonify({"error": "Model name is required"}), 400

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        frame_path = os.path.join(app.config['GENAI_FOLDER'], 'saved_frame.jpg')
        output_path = generate_synthetic_image_with_ip(prompt, frame_path, model_name)
        return jsonify({"message": "Synthetic image generated successfully", "output_path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_ai_story', methods=['POST'])
def generate_ai_story():
    logging.debug("Route hit: /generate_ai_story")
    try:
        # Get the stats folder from the request
        stats_folder = request.json.get('stats_folder')
        if not stats_folder:
            return jsonify({"error": "Statistics folder not provided"}), 400

        # Path to the overall_statistics.json file
        overall_stats_path = os.path.join(stats_folder, 'overall_statistics.json')

        # Check if the file exists
        if not os.path.exists(overall_stats_path):
            return jsonify({"error": "overall_statistics.json not found in the provided folder"}), 404

        # Load the overall statistics
        with open(overall_stats_path, 'r') as f:
            overall_stats = json.load(f)

        # Extract relevant data from the statistics to create a prompt
        # Example: Use the dominant emotion or other statistics as the prompt
        dominant_emotion = overall_stats.get('dominant_emotion', 'unknown')
        emotion_stats = overall_stats.get('emotion_stats', {})

        # Create a prompt based on the statistics
        prompt = f"In a financial domain where the dominant emotion is {dominant_emotion}, "
        prompt += f"with the following emotion distribution: {emotion_stats}, "
        prompt += "a story unfolds:"

        # Generate a story using the Hugging Face model
        generated_text = story_generator(prompt, max_length=200, num_return_sequences=1)
        story = generated_text[0]['generated_text']

        return jsonify({"message": "Story generated successfully", "story": story})
    except Exception as e:
        logging.error(f"Error in /generate_ai_story: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)