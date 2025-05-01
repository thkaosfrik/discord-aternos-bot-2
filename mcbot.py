import discord
from discord.ext import commands
import yt_dlp
import os
import subprocess
import asyncio
import requests  # Add this import for handling HTTP requests

# Set up the bot and define the command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# Queue to handle multiple requests
download_queue = asyncio.Queue()

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
        # Notify the user that the download is starting
        progress_message = await ctx.send("Starting download...")

        # Run yt-dlp in a separate thread
        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)

        # Simulate a moving loading symbol
        async def update_loading_symbol():
            symbols = ["|", "/", "-", "\\"]
            index = 0
            while not download_task.done():  # Keep updating until the download is complete
                await progress_message.edit(content=f"Downloading... {symbols[index]}")
                index = (index + 1) % len(symbols)  # Cycle through the symbols
                await asyncio.sleep(0.5)  # Update every 0.5 seconds

        # Create the download task
        download_task = asyncio.create_task(asyncio.to_thread(download_audio))

        # Run the loading symbol and download concurrently
        await asyncio.gather(download_task, update_loading_symbol())

        # Get the result of the download task
        info = download_task.result()

        # Delete the progress message once the download is complete
        await progress_message.delete()

        file_path = f'downloads/{info["id"]}.mp3'
        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds 10 MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            compressed_file_path = f'downloads/{info["id"]}_compressed.mp3'

            # Run ffmpeg compression in a separate thread
            def compress_audio():
                subprocess.run([
                    '/usr/bin/ffmpeg', '-i', file_path,
                    '-b:a', '128k', compressed_file_path
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
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save file to downloads folder
    }

    try:
        # Notify the user that the download is starting
        progress_message = await ctx.send("Starting download...")

        # Run yt-dlp in a separate thread
        def download_video():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)

        # Simulate a moving loading symbol
        async def update_loading_symbol():
            symbols = ["|", "/", "-", "\\"]
            index = 0
            while not download_task.done():  # Keep updating until the download is complete
                await progress_message.edit(content=f"Downloading... {symbols[index]}")
                index = (index + 1) % len(symbols)  # Cycle through the symbols
                await asyncio.sleep(0.5)  # Update every 0.5 seconds

        # Create the download task
        download_task = asyncio.create_task(asyncio.to_thread(download_video))

        # Run the loading symbol and download concurrently
        await asyncio.gather(download_task, update_loading_symbol())

        # Get the result of the download task
        info = download_task.result()

        # Debug: Log the info object (truncate if too large)
        debug_info = str(info)
        if len(debug_info) > 1000:  # Truncate if too long
            debug_info = debug_info[:1000] + "... (truncated)"
        await ctx.send(f"Debug: Download info: {debug_info}")

        # Delete the progress message once the download is complete
        await progress_message.delete()

        file_path = f'downloads/{info["id"]}.mp4'

        # Debug: Check if the file exists
        if not os.path.exists(file_path):
            # List the contents of the downloads directory for debugging
            downloads_dir = os.listdir('downloads')
            downloads_dir_str = "\n".join(downloads_dir)
            if len(downloads_dir_str) > 1000:  # Truncate if too long
                downloads_dir_str = downloads_dir_str[:1000] + "... (truncated)"
            await ctx.send(f"Debug: Downloads directory contents: {downloads_dir_str}")
            await ctx.send("The file could not be found. The download may have failed.")
            return

        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds 10 MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            compressed_file_path = f'downloads/{info["id"]}_compressed.mp4'

            # Compress the file using ffmpeg with more aggressive settings
            def compress_video():
                subprocess.run([
                    '/usr/bin/ffmpeg', '-i', file_path,
                    '-vf', 'scale=640:360',  # Scale video to 360p
                    '-b:v', '500k',          # Lower video bitrate to 500 kbps
                    '-b:a', '64k',           # Lower audio bitrate to 64 kbps
                    '-fs', '8M',             # Limit output file size to 8 MB
                    compressed_file_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Suppress ffmpeg output
                os.remove(file_path)  # Remove the original file
                return compressed_file_path

            file_path = await asyncio.to_thread(compress_video)

        # Check if the compressed file still exceeds Discord's limit
        if os.path.getsize(file_path) > 8 * 1024 * 1024:  # 8 MB in bytes
            os.remove(file_path)  # Clean up the file
            await ctx.send("The file is too large to upload to Discord, even after compression.")
        else:
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
