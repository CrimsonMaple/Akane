import os
import discord
import dropbox
from threading import Thread
import time
from yt_dlp import YoutubeDL
import re

"""
    AkaneBot, A simple discord bot designed to download youtube videos to convert to mp3.

    Author: Krystal V. (CrimsonMaple)
    License: BSD Version 3.
"""
#=======================================================================================
# Dropbox Connection.
#=======================================================================================
dropbox_client = dropbox.Dropbox
def dropbox_create_connection(dropbox_access_token):
    global dropbox_client
    dropbox_client = dropbox.Dropbox(dropbox_access_token)
    print("[NOTICE]: Dropbox connection is live.")

#=======================================================================================
# This is a complete hack, might want to rework this.
#=======================================================================================
default_client = discord.Client(intents=discord.Intents.default())


@default_client.event
async def say_hello(message):
    user = message.author
    g_channel = message.channel
    
    await g_channel.send(f"Hello, {user.mention}")

#=======================================================================================
# YT-DLP Helper Functions
#=======================================================================================

# Check if URL is a Youtube URL.
def validate_youtube_url(url):
    # Youtube link REGEX check.
    if url is not None and url != '':
        reg_exp = re.compile(r'^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$')
    
    # If the link is not a youtube link, alert the user.
    if not reg_exp.match(url):
        return False
    
    return True

# Validates the download's existance and returns path.
def fetch_music_path(folder_path):
    # Check file exists.
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    mp3_file = None

    # Find the mp3 file in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_file = (os.path.join(root, file), os.path.splitext(file)[0])
                break
        if mp3_file:
            break

    if mp3_file:
        # Return File Path
        return mp3_file
    else:
        print("No mp3 file found in the 'song' folder.")

# Limited storage device, delete all songs at midnight.
def song_cleaner(dropbox_path):
    # Delete local file in 5 minutes.
    time.sleep(30 * 60)
    print(f"deleting file @ {dropbox_path}")
    dropbox_client.files_delete(dropbox_path)

    

# Downloads a Youtube Link using YT-DLP converts the contents to MP3 and uploads to discord
@default_client.event
async def yt_dlp(message):
    # Setup
    user = message.author
    g_channel = message.channel

    url = message.content

    # Get youtube link out of text and check if its valid.
    url = url[7:]
    if not validate_youtube_url(url):
        await g_channel.send(f'{user.mention}! I think the link may be incorrect..."')
        return
    
    # Setup yt-dlp arguments.
    ydl_opts = {
    'format': 'mp3/bestaudio/best',

    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],

    'outtmpl': os.path.join(os.getcwd(), 'song/%(title)s.%(ext)s')
    }

    # Checking output path for linux bug.
    print(ydl_opts)

    # Link is valid feed it into yt-dlp.
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)


    # Zip song and ship it off to discord.
    music_path = os.path.join(os.getcwd(), "song")
    mp3_file = fetch_music_path(music_path)

    # BETA: Dropbox File Upload.
    dropbox_path = "/AkaneBot/" + mp3_file[1] + ".mp3"
    computer_path = mp3_file[0]

    # Upload file to dropbox
    try:
        dropbox_client.files_upload(open(computer_path, "rb").read(), dropbox_path)
        print("[UPLOADED] {}".format(computer_path))
        
    except Exception as e:
        print(e)
    
    os.remove(computer_path)

    # Get download link from dropbox.
    song_link = dropbox_client.files_get_temporary_link(dropbox_path)
    
    # send dropbox link.
    await g_channel.send(f"Here's the song for you!~\nIt will be live for 30 minutes!~\n\n{song_link.link}")

    # Spawn task to delete song in 30 minutes.
    cleaner_thread = Thread(target=song_cleaner, args=[dropbox_path])
    cleaner_thread.start()

@default_client.event
async def help_message(message):
    g_channel = message.channel

    help_messages = {
                     "!hello"      : "Send a reply!",
                     "!fetch"      : "Grabs a Youtube Video and Converts it to MP3.",
                     "!help"       : "Display this message!"}
    for command in help_messages:
        await g_channel.send(f"{command} - {help_messages[command]}")

# =======================================================================================
