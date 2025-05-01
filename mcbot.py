import discord
from discord.ext import commands
import os
import subprocess
import uuid
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command()
async def c3(ctx, url: str):
    await handle_download(ctx, url, "mp3")

@bot.command()
async def c4(ctx, url: str):
    await handle_download(ctx, url, "mp4")

async def handle_download(ctx, url, format):
    await ctx.send(f"Downloading as {format.upper()}...")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{format}"
    ytdlp_cmd = [
        "yt-dlp",
        url,
        "-f", "bestaudio" if format == "mp3" else "best",
        "-o", filename
    ]

    if format == "mp3":
        ytdlp_cmd += ["--extract-audio", "--audio-format", "mp3"]

    try:
        subprocess.run(ytdlp_cmd, check=True)

        if os.path.exists(filename):
            await ctx.send(file=discord.File(filename))
            os.remove(filename)
        else:
            await ctx.send("Download failed: File not found.")
    except subprocess.CalledProcessError:
        await ctx.send("Download failed. Invalid URL or server error.")

bot.run(TOKEN)