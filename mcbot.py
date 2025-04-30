import os
import requests
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get environment variables
TOKEN = os.getenv("TOKEN")
Aternos_USERNAME = os.getenv("USERNAME")
Aternos_PASSWORD = os.getenv("PASSWORD")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Set up the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Aternos API base URL
BASE_URL = "https://aternos.org/api/v1/"

# Function to login to Aternos and retrieve a token
def aternos_login(username, password):
    login_url = BASE_URL + "login"
    login_data = {"username": username, "password": password}
    response = requests.post(login_url, data=login_data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Login failed!")
        return None

# Function to get server status
def get_server_status(token):
    server_url = BASE_URL + "server"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(server_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch server status")
        return None

# Function to start the Aternos server
def start_server(token):
    start_url = BASE_URL + "server/start"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(start_url, headers=headers)
    
    if response.status_code == 200:
        print("Server started!")
        return True
    else:
        print("Failed to start server")
        return False

# Function to stop the Aternos server
def stop_server(token):
    stop_url = BASE_URL + "server/stop"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(stop_url, headers=headers)
    
    if response.status_code == 200:
        print("Server stopped!")
        return True
    else:
        print("Failed to stop server")
        return False

# Function to restart the Aternos server
def restart_server(token):
    restart_url = BASE_URL + "server/restart"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(restart_url, headers=headers)
    
    if response.status_code == 200:
        print("Server restarted!")
        return True
    else:
        print("Failed to restart server")
        return False

# Function to create the status message with buttons
async def create_status_message(channel):
    # Create the buttons
    start_button = Button(label="Start", style=discord.ButtonStyle.green)
    stop_button = Button(label="Stop", style=discord.ButtonStyle.red)
    restart_button = Button(label="Restart", style=discord.ButtonStyle.blurple)

    # Button interaction callbacks
    async def start_callback(interaction):
        login_response = aternos_login(Aternos_USERNAME, Aternos_PASSWORD)
        if login_response:
            token = login_response.get("token")
            if start_server(token):
                await interaction.response.edit_message(content="Server started!")
            else:
                await interaction.response.edit_message(content="Failed to start server.")

    async def stop_callback(interaction):
        login_response = aternos_login(Aternos_USERNAME, Aternos_PASSWORD)
        if login_response:
            token = login_response.get("token")
            if stop_server(token):
                await interaction.response.edit_message(content="Server stopped!")
            else:
                await interaction.response.edit_message(content="Failed to stop server.")
    
    async def restart_callback(interaction):
        login_response = aternos_login(Aternos_USERNAME, Aternos_PASSWORD)
        if login_response:
            token = login_response.get("token")
            if restart_server(token):
                await interaction.response.edit_message(content="Server restarted!")
            else:
                await interaction.response.edit_message(content="Failed to restart server.")

    # Assign the callbacks to the buttons
    start_button.callback = start_callback
    stop_button.callback = stop_callback
    restart_button.callback = restart_callback

    # Create a view with the buttons
    view = View()
    view.add_item(start_button)
    view.add_item(stop_button)
    view.add_item(restart_button)

    # Send the message with the buttons
    message = await channel.send("Server is offline", view=view)
    return message

# Event that triggers when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

    # Get the channel to send the message
    channel = bot.get_channel(CHANNEL_ID)

    # Login to Aternos and get the token
    login_response = aternos_login(Aternos_USERNAME, Aternos_PASSWORD)
    if login_response:
        token = login_response.get("token")
        
        # Get the server status
        status = get_server_status(token)

        # Send the status message and create buttons
        if status:
            server_status = "online" if status['online'] else "offline"
            message = await create_status_message(channel)
            await message.edit(content=f"Server is {server_status}")

# Function to update the status message regularly
async def update_status_message():
    channel = bot.get_channel(CHANNEL_ID)
    login_response = aternos_login(Aternos_USERNAME, Aternos_PASSWORD)
    if login_response:
        token = login_response.get("token")
        status = get_server_status(token)
        server_status = "online" if status['online'] else "offline"
        message = await channel.fetch_message(channel.last_message_id)
        await message.edit(content=f"Server is {server_status}")

# Run the bot with the provided token
bot.run(TOKEN)