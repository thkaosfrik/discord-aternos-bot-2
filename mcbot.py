import discord
from discord.ext import tasks, commands
from discord import app_commands
from aternos import Client
import asyncio
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

status_message = None
aternos_server = None
notifiers = set()


class ServerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🟢 Starting server...", ephemeral=True)
        notifiers.add(interaction.user.id)
        aternos_server.start()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔴 Stopping server...", ephemeral=True)
        aternos_server.stop()

    @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary)
    async def restart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔄 Restarting server...", ephemeral=True)
        aternos_server.restart()


async def get_server_status():
    status = aternos_server.status
    address = aternos_server.address
    players = ""

    if status.lower() == "online":
        try:
            players = aternos_server.players
            players_list = ", ".join(players["list"]) if players["count"] > 0 else "No players online"
            players = f"\n👥 **Players ({players['count']})**: {players_list}"
        except Exception:
            players = "\n👥 Could not fetch players."
    return f"🌐 **Aternos Server Status:** `{status}`\n🔗 **IP:** `{address}`{players}"


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        await tree.sync()
    except Exception as e:
        print(f"Slash command sync failed: {e}")

    global aternos_server
    at_client = Client.from_credentials(USERNAME, PASSWORD)
    servers = at_client.list_servers()
    aternos_server = servers[0]

    channel = bot.get_channel(CHANNEL_ID)
    global status_message

    async for msg in channel.history(limit=50):
        if msg.author == bot.user and msg.components:
            status_message = msg
            break

    if not status_message:
        status_text = await get_server_status()
        status_message = await channel.send(status_text, view=ServerView())
    else:
        await status_message.edit(view=ServerView())

    update_status.start()


@tasks.loop(seconds=30)
async def update_status():
    if not status_message:
        return

    current_status = aternos_server.status
    content = await get_server_status()
    await status_message.edit(content=content)

    if current_status.lower() == "online":
        for user_id in list(notifiers):
            user = await bot.fetch_user(user_id)
            try:
                await user.send(f"✅ The Aternos server is now online!\nIP: `{aternos_server.address}`")
            except discord.Forbidden:
                print(f"Couldn't DM user {user.name}")
            notifiers.remove(user_id)


@tree.command(name="status", description="Show current Aternos server status")
async def status_command(interaction: discord.Interaction):
    status = await get_server_status()
    await interaction.response.send_message(status, ephemeral=True)


bot.run(TOKEN)