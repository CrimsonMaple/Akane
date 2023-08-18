import os
import discord
from yt_dlp import YoutubeDL
import re



"""
    AkaneBot, A simple discord bot designed to download youtube videos to convert to mp3.

    Author: Krystal V. (CrimsonMaple)
    License: BSD Version 3.
"""

#=======================================================================================
# This is a complete hack, might want to rework this.
#=======================================================================================
default_client = discord.Client(intents=discord.Intents.default())


@default_client.event
async def say_hello(message):
    user = message.author
    g_channel = message.channel
    
    await g_channel.send(f"Hello, {user.mention}")

def validate_youtube_url(url):
    # Check if URL is a Youtube URL.
    if url is not None and url != '':
        reg_exp = re.compile(r'^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$')
    
    # If the link is not a youtube link, alert the user.
    if not reg_exp.match(url):
        return False
    
    return True
        

def fetch_music_path(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    mp3_file = None

    # Find the mp3 file in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_file = os.path.join(root, file)
                break
        if mp3_file:
            break

    if mp3_file:
        # Return File Path
        return mp3_file
    else:
        print("No mp3 file found in the 'song' folder.")

@default_client.event
async def yt_dlp(message):
    # TODO: Download a Youtube Link using YT-DLP.
    # TODO: Convert video to MP3 using FFMPEG.
    # TODO: Zip the contents and upload to Discord FS.
    user = message.author
    g_channel = message.channel

    url = message.content

    # Get youtube link out of text and check if its valid.
    url = url[7:]
    if not validate_youtube_url(url):
        await g_channel.send(f'{user.mention}! Master! I think the link may be incorrect..."')
        return
    
    # Setup yt-dlp arguments.
    ydl_opts = {
    'format': 'mp3/bestaudio/best',

    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],

    'outtmpl': '/song/%(title)s.%(ext)s'
    }

    
    # Link is valid feed it into yt-dlp.
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)


    # Zip song and ship it off to discord.
    music_path = os.path.join(os.getcwd(), "song")
    mp3_file = fetch_music_path(music_path)

    await g_channel.send("Here's the song for you master!~", file=discord.File(mp3_file))
    
    # Delete song when we're done.
    os.remove(mp3_file)



@default_client.event
async def help_message(message):
    g_channel = message.channel

    help_messages = {
                     "!hello"      : "Send a reply!",
                     "!fetch"        : "Grabs a Youtube Video and Converts it to MP3.",
                     "!help"       : "Display this message!"}
    for command in help_messages:
        await g_channel.send(f"{command} - {help_messages[command]}")

# =======================================================================================
