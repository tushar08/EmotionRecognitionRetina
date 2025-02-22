let uploadedVideoBlob = null;
let savedFrameData = null;
let syntheticImageData = null;

// Function to upload video
async function uploadVideo() {
    const fileInput = document.getElementById('videoFile');
    if (fileInput.files.length === 0) {
        alert("Please select a video file.");
        return;
    }

    const file = fileInput.files[0];
    uploadedVideoBlob = new Blob([file], { type: file.type });

    // Display the uploaded video
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.src = URL.createObjectURL(uploadedVideoBlob);
    videoPlayer.style.display = 'block';
    document.getElementById('webcamPreview').style.display = 'none';

    alert("Video uploaded successfully. Click 'Generate Statistics' to analyze.");
}

// Function to generate statistics
async function generateStatistics() {
    if (!uploadedVideoBlob) {
        alert("Please upload a video first.");
        return;
    }

    const frameInterval = document.getElementById('frameInterval').value;
    const statsOutput = document.getElementById('statsOutput');
    const storyOutput = document.getElementById('storyOutput');
    const loader = document.getElementById('loader');

    // Show loader
    loader.style.display = 'block';
    statsOutput.innerHTML = '';
    storyOutput.innerHTML = '';

    const formData = new FormData();
    formData.append('video', uploadedVideoBlob, 'uploaded_video.mp4');
    formData.append('frame_interval', frameInterval);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        console.log("Server response (upload):", result); // Log the upload response

        if (response.ok) {
            // Fetch and display statistics
            const statsResponse = await fetch(`/get_stats?stats_folder=${result.stats_folder}`);
            const stats = await statsResponse.json();
            console.log("Statistics data:", stats); // Log the statistics data

            // Ensure stats is an object before passing it to displayStats
            if (stats && typeof stats === 'object' && !Array.isArray(stats)) {
                displayStats(stats);
                displayStory(stats);
            } else {
                statsOutput.textContent = "Invalid statistics data received from the server.";
            }
        } else {
            statsOutput.textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        statsOutput.textContent = `Error: ${error.message}`;
    } finally {
        // Hide loader
        loader.style.display = 'none';
    }
}

// Function to generate AI story
async function generateAIStory() {
    const storyOutput = document.getElementById('storyOutput');
    const loader = document.getElementById('loader');

    // Show loader
    loader.style.display = 'block';
    storyOutput.innerHTML = '';

    try {
        const response = await fetch('/generate_ai_story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ video_data: uploadedVideoBlob })
        });

        const result = await response.json();
        if (response.ok) {
            storyOutput.innerHTML = `<p>${result.story}</p>`;
        } else {
            storyOutput.textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        storyOutput.textContent = `Error: ${error.message}`;
    } finally {
        // Hide loader
        loader.style.display = 'none';
    }
}

// Function to toggle visibility of statistics
function toggleStats(faceId) {
    const statsElement = document.getElementById(`stats-${faceId}`);
    if (statsElement.style.display === "none" || !statsElement.style.display) {
        statsElement.style.display = "block";
    } else {
        statsElement.style.display = "none";
    }
}


// Function to display the story
function displayStory(stats) {
    const storyOutput = document.getElementById('storyOutput');
    storyOutput.innerHTML = '';

    // Check if stats is defined and is an object
    if (!stats || typeof stats !== 'object' || Array.isArray(stats)) {
        storyOutput.textContent = "No story available due to invalid data.";
        return;
    }

    // Check if stats has at least one face
    if (Object.keys(stats).length === 0) {
        storyOutput.textContent = "No faces detected in the video.";
        return;
    }

    let story = "";

    // Iterate over the stats object
    for (const [faceId, data] of Object.entries(stats)) {
        const mostCommonEmotion = data.most_common_emotion;
        const emotionCounts = data.emotion_counts;
        const averageConfidences = data.average_confidences;
        const averageAge = data.average_age;
        const averageRace = data.average_race;

        if (averageAge > 0 && 1==2) {
            story += `<p><strong>Face ${faceId}:</strong> `;
            story += `This person appears to be around <strong>${Math.round(averageAge)} years old</strong>. `;

            // Check if averageRace is defined and is an object
            if (averageRace && typeof averageRace === 'object' && Object.keys(averageRace).length > 0) {
                const predominantRace = Object.keys(averageRace).reduce((a, b) => averageRace[a] > averageRace[b] ? a : b);
                story += `Their predominant racial identity is <strong>${predominantRace}</strong>. `;
            } else {
                story += `Their racial identity could not be determined. `;
            }

            // Check if emotionCounts and mostCommonEmotion are defined
            if (emotionCounts && mostCommonEmotion && emotionCounts[mostCommonEmotion]) {
                story += `The most common emotion detected was <strong>${mostCommonEmotion}</strong>. `;
                story += `This emotion appeared in <strong>${emotionCounts[mostCommonEmotion]}</strong> out of <strong>${data.total_frames_processed}</strong> frames. `;
            } else {
                story += `The most common emotion could not be determined. `;
            }

            // Check if averageConfidences and mostCommonEmotion are defined
            if (averageConfidences && mostCommonEmotion && averageConfidences[mostCommonEmotion]) {
                story += `The average confidence for this emotion was <strong>${averageConfidences[mostCommonEmotion].toFixed(2)}%</strong>. `;
            } else {
                story += `The average confidence for this emotion could not be determined. `;
            }

            if (mostCommonEmotion === "happy") {
                story += `This suggests that the person was generally in a positive and cheerful mood. `;
            } else if (mostCommonEmotion === "sad") {
                story += `This indicates that the person was often feeling down or melancholic. `;
            } else if (mostCommonEmotion === "angry") {
                story += `This points to moments of frustration or anger. `;
            } else if (mostCommonEmotion === "surprise") {
                story += `This shows that the person was frequently surprised or startled. `;
            } else if (mostCommonEmotion === "neutral") {
                story += `This suggests that the person was mostly calm and composed. `;
            }

            // Check if emotionCounts is a non-empty object
            if (emotionCounts && typeof emotionCounts === 'object' && Object.keys(emotionCounts).length > 0) {
                const otherEmotions = Object.keys(emotionCounts).filter(e => e !== mostCommonEmotion);
                if (otherEmotions.length > 0) {
                    const otherEmotionsString = otherEmotions
                        .map(e => {
                            // Check if emotionCounts[e] is defined
                            if (emotionCounts[e] !== undefined) {
                                return `<strong>${e}</strong> (${emotionCounts[e]} frames)`;
                            } else {
                                return null; // Skip this emotion if the count is undefined
                            }
                        })
                        .filter(Boolean) // Remove null values from the array
                        .join(", ");

                    if (otherEmotionsString.length > 0) {
                        story += `Other emotions detected include: ${otherEmotionsString}. `;
                    }
                }
            }

            // Add face interactions
            if (data.interactions && data.interactions.length > 0 && data.interactions[0]) {
                story += `This person interacted with other faces in the video. `;
                story += `For example, they were seen interacting with <strong>Face ${data.interactions[0].with_face}</strong> for <strong>${data.interactions[0].duration} seconds</strong>, during which their emotion was predominantly <strong>${data.interactions[0].emotion}</strong>. `;
            }

            story += `</p>`;
        }
    }

    storyOutput.innerHTML = story;
}

// Function to save frame
async function saveFrame() {
    const videoPlayer = document.getElementById('videoPlayer');
    const canvas = document.createElement('canvas');
    canvas.width = videoPlayer.videoWidth;
    canvas.height = videoPlayer.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);

    // Convert the canvas image to a base64-encoded string
    const frameData = canvas.toDataURL('image/jpeg');

    try {
        const response = await fetch('/save_frame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ frame_data: frameData })
        });

        const result = await response.json();
        if (response.ok) {
            // Display the saved frame
            const savedFrame = document.getElementById('savedFrame');
            savedFrame.src = frameData;
            savedFrame.style.display = 'block';
            alert(`Frame saved successfully: ${result.frame_path}`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Function to generate synthetic image
async function generateImage() {
    const modelName = document.getElementById('modelName').value;
    const prompt = document.getElementById('promptInput').value;

    if (!modelName) {
        alert("Please enter a valid model name.");
        return;
    }

    if (!prompt) {
        alert("Please enter a prompt.");
        return;
    }

    try {
        const response = await fetch('/generate_synthetic_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ model_name: modelName, prompt: prompt })
        });

        const result = await response.json();
        if (response.ok) {
            // Display the synthetic image
            const syntheticImage = document.getElementById('syntheticImage');
            syntheticImage.src = result.output_path;
            syntheticImage.style.display = 'block';
            alert(`Synthetic image generated successfully: ${result.output_path}`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Function to train generative model
async function trainModel() {
    try {
        const response = await fetch('/train_generative_model', {
            method: 'POST'
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Generative model trained successfully: ${result.model_path}`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Function to login to Hugging Face
async function loginHuggingFace() {
    const token = document.getElementById('hfToken').value;
    if (!token) {
        alert("Please enter a Hugging Face token.");
        return;
    }

    try {
        const response = await fetch('/login_huggingface', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Function to display statistics in a vertical layout
function displayStats(stats) {
    const statsOutput = document.getElementById('statsOutput');
    statsOutput.innerHTML = '';

    // Check if stats is defined and is an object
    if (!stats || typeof stats !== 'object' || Array.isArray(stats)) {
        statsOutput.textContent = "No statistics available or invalid data format.";
        return;
    }

    // Check if stats has at least one face
    if (Object.keys(stats).length === 0) {
        statsOutput.textContent = "No faces detected in the video.";
        return;
    }

    // Iterate over the stats object
    for (const [faceId, data] of Object.entries(stats)) {
        const faceContainer = document.createElement('div');
        faceContainer.className = 'face-container';

        // Display thumbnail
        if (data.thumbnails && data.thumbnails.length > 0) {
            const thumbnail = document.createElement('img');
            thumbnail.src = `data:image/jpeg;base64,${data.thumbnails[0]}`;
            thumbnail.className = 'face-thumbnail';
            faceContainer.appendChild(thumbnail);
        }

        // Display face ID
        const faceHeader = document.createElement('div');
        faceHeader.className = 'face-header';
        faceHeader.innerHTML = `<strong>Face ${faceId}</strong>`;
        faceContainer.appendChild(faceHeader);

        // Display story
        const story = generateStoryForFace(data);
        const storyDiv = document.createElement('div');
        storyDiv.className = 'face-story';
        storyDiv.innerHTML = story;
        faceContainer.appendChild(storyDiv);

        // Toggle button for detailed statistics
        const toggleButton = document.createElement('button');
        toggleButton.textContent = "Show Statistics";
        toggleButton.onclick = () => toggleStats(faceId);
        faceContainer.appendChild(toggleButton);

        // Detailed statistics (hidden by default)
        const statsDiv = document.createElement('pre');
        statsDiv.id = `stats-${faceId}`;
        statsDiv.className = 'face-stats';
        statsDiv.textContent = JSON.stringify(data, null, 2);
        statsDiv.style.display = 'none'; // Initially hidden
        faceContainer.appendChild(statsDiv);

        statsOutput.appendChild(faceContainer);
    }
}

// Function to generate story for a single face
function generateStoryForFace(data) {
    let story = "";

    const mostCommonEmotion = data.most_common_emotion;
    const emotionCounts = data.emotion_counts;
    const averageConfidences = data.average_confidences;
    const averageAge = data.average_age;
    const averageRace = data.average_race;
    const mostCommonGender = data.most_common_gender;
    if (averageAge > 0) {
        story += `<p><strong>Face ${data.faceId}:</strong> `;
        story += `This person appears seems to a <strong>${mostCommonGender}</strong> and to be around <strong>${Math.round(averageAge)} years old</strong>. `;

        if (averageRace && typeof averageRace === 'object' && Object.keys(averageRace).length > 0) {
            const predominantRace = Object.keys(averageRace).reduce((a, b) => averageRace[a] > averageRace[b] ? a : b);
            story += `Their predominant racial identity is <strong>${predominantRace}</strong>. `;
        } else {
            story += `Their racial identity could not be determined. `;
        }

        if (emotionCounts && mostCommonEmotion && emotionCounts[mostCommonEmotion]) {
            story += `The most common emotion detected was <strong>${mostCommonEmotion}</strong>. `;
            story += `This emotion appeared in <strong>${emotionCounts[mostCommonEmotion]}</strong> out of <strong>${data.total_frames_processed}</strong> frames. `;
        } else {
            story += `The most common emotion could not be determined. `;
        }

        if (averageConfidences && mostCommonEmotion && averageConfidences[mostCommonEmotion]) {
            story += `The average confidence for this emotion was <strong>${averageConfidences[mostCommonEmotion].toFixed(2)}%</strong>. `;
        } else {
            story += `The average confidence for this emotion could not be determined. `;
        }

        if (mostCommonEmotion === "happy") {
            story += `This suggests that the person was generally in a positive and cheerful mood. `;
        } else if (mostCommonEmotion === "sad") {
            story += `This indicates that the person was often feeling down or melancholic. `;
        } else if (mostCommonEmotion === "angry") {
            story += `This points to moments of frustration or anger. `;
        } else if (mostCommonEmotion === "surprise") {
            story += `This shows that the person was frequently surprised or startled. `;
        } else if (mostCommonEmotion === "neutral") {
            story += `This suggests that the person was mostly calm and composed. `;
        }

        if (emotionCounts && typeof emotionCounts === 'object' && Object.keys(emotionCounts).length > 0) {
            const otherEmotions = Object.keys(emotionCounts).filter(e => e !== mostCommonEmotion);
            if (otherEmotions.length > 0) {
                const otherEmotionsString = otherEmotions
                    .map(e => {
                        if (emotionCounts[e] !== undefined) {
                            return `<strong>${e}</strong> (${emotionCounts[e]} frames)`;
                        } else {
                            return null;
                        }
                    })
                    .filter(Boolean)
                    .join(", ");

                if (otherEmotionsString.length > 0) {
                    story += `Other emotions detected include: ${otherEmotionsString}. `;
                }
            }
        }

        if (data.interactions && data.interactions.length > 0 && data.interactions[0]) {
            story += `This person interacted with other faces in the video. `;
            story += `For example, they were seen interacting with <strong>Face ${data.interactions[0].with_face}</strong> for <strong>${data.interactions[0].duration} seconds</strong>, during which their emotion was predominantly <strong>${data.interactions[0].emotion}</strong>. `;
        }

        story += `</p>`;
    }
    return story;
}

// Function to toggle visibility of statistics
function toggleStats(faceId) {
    const statsElement = document.getElementById(`stats-${faceId}`);
    if (statsElement.style.display === "none" || !statsElement.style.display) {
        statsElement.style.display = "block";
    } else {
        statsElement.style.display = "none";
    }
}