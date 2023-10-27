import discord
import commands as Akane

"""
    AkaneBot, A simple discord bot designed to download youtube videos to convert to mp3.

    Author: Krystal V. (CrimsonMaple)
    License: BSD Version 3.
"""


def parse_config(path):
    """
    A function for reading the configuration and returning the configuration data
    :param path: the path and filename of the configuration file
    :return: A dictionary containing the configuration information
    """
    fp = open(path, "r")
    # Store config data in a dictionary, with the key being the type.
    data = dict()

    # Loop through the file and split at separators.
    for line in fp:
        tmp = list()
        tmp += line.split(": ")

        # Can be expanded in the future.
        if tmp[0].strip() == "token":
            data["token"] = tmp[1].strip()
        if tmp[0].strip() == "dropbox":
            data["dropbox"] = tmp[1].strip()

    return data


class akane_client(discord.Client):
    """
    A class for handling client calls such as on_ready and on_message
    """
    async def on_ready(self):
        """
        On ready, ping the terminal that bot is connected.
        :return: None
        """
        print(self.user, "has been connected successfully!~")

    async def on_message(self, message):
        """
        The function that handles incoming messages. It checks for commands and calls the corresponding function
        :param message: a message object representing the message that was just sent
        :return: None
        """
        try:
            # Don't trigger on own user.
            if message.author == self.user:
                return

            # Store the message
            text = message.content.lower()
            command = ""

            # basic command
            if text != "" and text[0] == "!":
                # Split String for command args.
                args = text[1:].split()
                print (args)

                # Set containing the possible client commands.
                # TODO: Move this out of this class and make global.
                operation = {"hello"      : Akane.say_hello,
                             "fetch"      : Akane.yt_dlp,
                             "help"       : Akane.help_message
                             }

                # If the command is in the set, then launch the command.
                if args[0] in operation:
                    await operation[args[0]](message)

        except Exception as e:
            await message.channel.send(f"*There's a huge problem!\n\n{e}")


def akane_bot():
    """
    Basically the main function. Parses the config and starts the bot
    :return: None
    """
    # Hello World!
    print("Akane at your service, Master!\n")

    # Open my config, and read out he token.
    config = parse_config("config.txt")
    print("Akane is being loaded using token:", config["token"])

    # Connect in Dropbox
    Akane.dropbox_create_connection(config["dropbox"])
    print(f"Dropbox is using this token: {config['dropbox']}")

    # Launch the client
    client = akane_client(intents=discord.Intents(messages=True, message_content=True))

    # Run the bot.
    client.run(config["token"])


# Akane do the thing.
if __name__ == "__main__":
    akane_bot()
