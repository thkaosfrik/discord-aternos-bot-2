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
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Ensure ffmpeg is correctly located
        'format': 'bestaudio/best',  # Download best audio quality
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Audio quality
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save file to downloads folder
    }

    # Use yt-dlp to download the audio from the YouTube link and convert it
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Send the MP3 file to Discord
    await ctx.send(file=discord.File(f'downloads/{info["id"]}.mp3'))

# Command to convert YouTube video to MP4
@bot.command()
async def c4(ctx, url: str):
    # Define the options for yt-dlp
    ydl_opts = {
        'ffmpeg_location': '/usr/bin/ffmpeg',
        'format': 'bestvideo+bestaudio/best',  # Download best video and audio quality
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferredcodec': 'mp4',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    # Use yt-dlp to download the video and convert it to MP4
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Send the MP4 file to Discord
    await ctx.send(file=discord.File(f'downloads/{info["id"]}.mp4'))

# Run the bot with your token
bot.run(os.getenv('DISCORD_TOKEN'))