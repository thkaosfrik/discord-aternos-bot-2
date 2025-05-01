import discord
from discord.ext import commands
import yt_dlp
import os

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# Download and convert YouTube video to MP3 or MP4
@bot.command(name='c3')
async def convert_to_mp3(ctx, url: str):
    await ctx.send("Downloading MP3...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

@bot.command(name='c4')
async def convert_to_mp4(ctx, url: str):
    await ctx.send("Downloading MP4...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

# Start the bot using the token from the environment variable
bot.run(os.getenv('DISCORD_TOKEN'))