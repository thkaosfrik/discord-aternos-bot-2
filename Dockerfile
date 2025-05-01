# Use a base image that supports Python and includes apt
FROM python:3.12-slim

# Install ffmpeg (necessary for audio/video processing)
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code to the container
COPY . /app/

# Command to run the bot
CMD ["python", "mcbot.py"]