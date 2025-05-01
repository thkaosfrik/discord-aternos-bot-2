# Use the official Python image as a base
FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . /app/

# Set the environment variable for FFmpeg location
ENV FFMPEG_LOCATION=/usr/bin/ffmpeg

# Command to run the bot
CMD ["python", "mcbot.py"]