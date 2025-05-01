import discord
from discord.ext import commands
import yt_dlp
import os

# Set up the bot and define the command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# Command to convert YouTube video to MP3
@bot.command()
async def c3(ctx, url: str):
    # Define the options for yt-dlp
    ydl_opts = {
        'ffmpeg_location': 'ffmpeg',  # Use global ffmpeg
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

        # Send the MP3 file to Discord
        await ctx.send(file=discord.File(f'downloads/{info["id"]}.mp3'))

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Command to convert YouTube video to MP4
@bot.command()
async def c4(ctx, url: str):
    # Define the options for yt-dlp
    ydl_opts = {
        'ffmpeg_location': 'ffmpeg',  # Use global ffmpeg
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

        # Send the MP4 file to Discord
        await ctx.send(file=discord.File(f'downloads/{info["id"]}.mp4'))

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot with your token
bot.run(os.getenv('DISCORD_TOKEN'))
