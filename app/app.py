from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from utils.emotion_detection import process_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATS_FOLDER'] = 'emotion_stats'

# Ensure upload and stats folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATS_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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

    # Process the video
    stats_folder = os.path.join(app.config['STATS_FOLDER'], os.path.splitext(video_file.filename)[0])
    process_video(video_path, stats_folder)

    return jsonify({"message": "Video processed successfully", "stats_folder": stats_folder})

@app.route('/stats/<filename>')
def get_stats(filename):
    stats_folder = os.path.join(app.config['STATS_FOLDER'], filename)
    if not os.path.exists(stats_folder):
        return jsonify({"error": "Statistics not found"}), 404

    # Load and return the statistics
    stats_files = [f for f in os.listdir(stats_folder) if f.endswith('.json')]
    stats = {}
    for stats_file in stats_files:
        with open(os.path.join(stats_folder, stats_file), 'r') as f:
            stats[stats_file] = json.load(f)

    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
