# Emotion Detection from Video

This project is a Dockerized Flask application that detects emotions from faces in a video using **RetinaFace** for face detection and **DeepFace** for emotion analysis. The application provides a user-friendly interface for uploading videos or recording via webcam, and it displays detailed statistics about the detected emotions. Additionally, it includes **Generative AI** components to enhance emotion detection or generate synthetic data for training.

---

## Table of Contents
1. [Features](#features)
2. [Libraries Used](#libraries-used)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Running the Application](#running-the-application)
6. [How It Works](#how-it-works)
7. [Generative AI Components](#generative-ai-components)
8. [API Endpoints](#api-endpoints)
9. [Frontend UI](#frontend-ui)
10. [Dockerization](#dockerization)
11. [Contributing](#contributing)
12. [License](#license)

---

## Features
- **Video Upload**: Users can upload video files through a web interface.
- **Webcam Recording**: Users can record videos via their webcam.
- **Face Detection**: Uses **RetinaFace** to detect faces in each frame of the video.
- **Emotion Analysis**: Uses **DeepFace** to analyze emotions for each detected face.
- **Statistics Generation**: Generates detailed statistics for each face, including:
  - Count of all emotions.
  - Most common emotion.
  - Average confidence for each emotion.
  - Total frames processed.
  - Probabilistic embeddings shape.
  - Example embedding (first frame).
- **JSON Output**: Saves statistics and embeddings in JSON files for further analysis.
- **Generative AI Components**: Uses generative models to enhance emotion detection or generate synthetic data.
- **Dockerized**: The application is containerized using Docker for easy deployment.

---

## Libraries Used
- **Flask**: A lightweight web framework for Python used to create the backend API and serve the frontend.
- **OpenCV**: Used for video processing and frame extraction.
- **RetinaFace**: A state-of-the-art face detection model for accurately detecting faces in video frames.
- **DeepFace**: A deep learning-based facial analysis library used for emotion detection.
- **NumPy**: Used for numerical computations and handling arrays.
- **Diffusers**: For integrating generative AI models like Stable Diffusion.
- **Torch**: Used for GPU acceleration with generative AI models.
- **Docker**: Used to containerize the application for easy deployment and scalability.

---

## Project Structure
```
emotion-detection-app/
│
├── app/
│   ├── static/               # For CSS, JS, and other static files
│   ├── templates/            # For HTML templates
│   │   └── index.html        # Main UI template
│   ├── utils/                # Utility functions
│   │   ├── emotion_detection.py  # Emotion detection logic
│   │   └── generative_ai.py      # Generative AI logic
│   ├── app.py                # Flask backend
│
├── Dockerfile                # Dockerfile for containerization
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Setup and Installation

### Prerequisites
- **Docker**: Install Docker from [here](https://docs.docker.com/get-docker/).
- **Python**: Install Python 3.9 or later from [here](https://www.python.org/downloads/).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/emotion-detection-app.git
   cd emotion-detection-app
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Build the Docker image:
   ```bash
   docker build -t emotion-detection-app .
   ```

---

## Running the Application

### Using Docker
1. Run the Docker container:
   ```bash
   docker run -p 5000:5000 emotion-detection-app
   ```

2. Access the application at `http://localhost:5000`.

### Without Docker
1. Run the Flask application:
   ```bash
   python app/app.py
   ```

2. Access the application at `http://localhost:5000`.

---

## How It Works
1. **Video Upload**: The user uploads a video file through the web interface.
2. **Webcam Recording**: The user records a video via their webcam.
3. **Frame Extraction**: The application processes the video frame by frame.
4. **Face Detection**: **RetinaFace** detects faces in each frame.
5. **Emotion Analysis**: **DeepFace** analyzes emotions for each detected face.
6. **Statistics Generation**: The application generates statistics for each face and saves them in JSON files.
7. **Generative AI Enhancement**: Generative AI models are used to enhance emotion detection or generate synthetic data.
8. **Display Results**: The statistics are displayed on the web interface.

---

## Generative AI Components
The generative AI component of the project is implemented using **Diffusers** and **Stable Diffusion**. It can be used for two main purposes:

### 1. **Enhancing Emotion Detection**
- **Objective**: Use generative models to improve the accuracy of emotion detection by generating additional training data or refining predictions.
- **Process**:
  - Use a generative model (e.g., Stable Diffusion) to create synthetic facial expressions for underrepresented emotions.
  - Fine-tune the emotion detection model using the synthetic data.

### 2. **Generating Synthetic Data**
- **Objective**: Generate synthetic facial expressions to augment the training dataset for the emotion detection model.
- **Process**:
  - Use a generative model to create diverse facial expressions with different emotions.
  - Combine synthetic data with real data to train a more robust emotion detection model.

---

## API Endpoints
- **GET `/`**: Renders the main UI for uploading videos or recording via webcam.
- **POST `/upload`**: Accepts a video file and processes it for emotion detection.
- **POST `/record_video`**: Records a video via webcam and processes it for emotion detection.
- **GET `/get_stats`**: Returns the statistics for a processed video.
- **POST `/save_frame`**: Saves a specific frame for generative AI processing.
- **POST `/generate_synthetic_image`**: Generates a synthetic image using a generative AI model.

---

## Frontend UI
The frontend is a simple HTML page with the following features:
- **File Upload**: Users can upload video files.
- **Webcam Recording**: Users can record videos via their webcam.
- **Video Preview**: Displays the uploaded or recorded video.
- **Statistics Display**: Displays the generated statistics in a readable format.
- **Generative AI**: Users can generate synthetic images using generative AI models.

---

## Dockerization
The application is containerized using Docker for easy deployment. The `Dockerfile` includes:
- A base Python 3.9 image.
- Installation of dependencies from `requirements.txt`.
- Exposing port 5000 for the Flask application.
- Running the Flask app on container startup.

---

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
- **RetinaFace**: For accurate face detection.
- **DeepFace**: For emotion analysis.
- **Diffusers**: For generative AI models.
- **Flask**: For the backend API.
- **Docker**: For containerization.

---