import discord
from discord.ext import commands
import yt_dlp
import os
import subprocess
import asyncio

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
        # Run yt-dlp in a separate thread
        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)

        info = await asyncio.to_thread(download_audio)

        file_path = f'downloads/{info["id"]}.mp3'
        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds 10 MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            compressed_file_path = f'downloads/{info["id"]}_compressed.mp3'

            # Run ffmpeg compression in a separate thread
            def compress_audio():
                subprocess.run([
                    '/usr/bin/ffmpeg', '-i', file_path, '-b:a', '128k', compressed_file_path
                ])
                os.remove(file_path)  # Remove the original file
                return compressed_file_path

            file_path = await asyncio.to_thread(compress_audio)

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

            # Compress the file using ffmpeg with more aggressive settings
            def compress_video():
                subprocess.run([
                    '/usr/bin/ffmpeg', '-i', file_path,
                    '-vf', 'scale=1280:720',  # Scale video to 720p
                    '-b:v', '800k',          # Lower video bitrate to 800 kbps
                    '-b:a', '96k',           # Lower audio bitrate to 96 kbps
                    '-fs', '8M',             # Limit output file size to 8 MB
                    compressed_file_path
                ])
                os.remove(file_path)  # Remove the original file
                return compressed_file_path

            file_path = await asyncio.to_thread(compress_video)

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
