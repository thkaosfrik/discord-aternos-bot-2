import discord
from discord.ext import commands
import yt_dlp
import os
import subprocess

# Set up the bot and define the command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# Command to convert YouTube video to MP3
@bot.command()
async def c3(ctx, url: str):
    # Define the options for yt-dlp
    ydl_opts = {
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Explicit path to ffmpeg
        'format': 'bestaudio/best',  # Download best audio quality
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Correct key for audio extraction
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Audio quality
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save file to downloads folder
    }

    try:
        # Use yt-dlp to download the audio from the YouTube link and convert it
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        file_path = f'downloads/{info["id"]}.mp3'
        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds 10 MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            compressed_file_path = f'downloads/{info["id"]}_compressed.mp3'
            # Compress the file using ffmpeg
            subprocess.run([
                '/usr/bin/ffmpeg', '-i', file_path, '-b:a', '128k', compressed_file_path
            ])
            os.remove(file_path)  # Remove the original file
            file_path = compressed_file_path  # Use the compressed file instead

        # Send the (compressed) MP3 file to Discord
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)  # Clean up the file after sending

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Command to convert YouTube video to MP4
@bot.command()
async def c4(ctx, url: str):
    # Define the options for yt-dlp
    ydl_opts = {
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Explicit path to ffmpeg
        'format': 'bestvideo+bestaudio/best',  # Download best video and audio quality
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',  # Correct key for video conversion
            'preferredcodec': 'mp4',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    try:
        # Use yt-dlp to download the video and convert it to MP4
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        file_path = f'downloads/{info["id"]}.mp4'
        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds 10 MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            compressed_file_path = f'downloads/{info["id"]}_compressed.mp4'
            # Compress the file using ffmpeg
            subprocess.run([
                '/usr/bin/ffmpeg', '-i', file_path, '-vf', 'scale=1280:720', '-b:v', '1M', compressed_file_path
            ])
            os.remove(file_path)  # Remove the original file
            file_path = compressed_file_path  # Use the compressed file instead

        # Send the (compressed) MP4 file to Discord
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)  # Clean up the file after sending

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def check_ffmpeg(ctx):
    try:
        result = subprocess.run(['/usr/bin/ffmpeg', '-version'], capture_output=True, text=True)
        await ctx.send(f"FFmpeg is installed:\n{result.stdout}")
    except FileNotFoundError:
        await ctx.send("FFmpeg is not installed or not found.")

# Run the bot with your token
bot.run(os.getenv('DISCORD_TOKEN'))
