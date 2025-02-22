# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY packages /app/packages
RUN pip install --no-cache-dir --find-links=./packages --default-timeout=100 -r requirements.txt

# Copy the application code
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Run the application
CMD ["python", "app/app.py"]