# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify ffmpeg installation (optional for debugging)
RUN ffmpeg -version

# Expose the port the bot will run on (optional, for debugging purposes)
EXPOSE 8080

# Define environment variable for Railway
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "mcbot.py"]