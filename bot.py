import os
import random
import discord
import praw
import youtube_dl
from discord.ext import commands, ipc
from dotenv import load_dotenv
from GameRoom import GameRoom
from flask import Flask


app = Flask(__name__)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True

reddit = praw.Reddit(client_id="JSEQrmvt-zdUJg",
                     client_secret="XSa7-69NIBQUuA710spi4UNcZ36OGQ",
                     username="BlindPick0",
                     password="BlindPick0",
                     user_agent="BlindPick", check_for_async=False)

game_dict = {}


class client(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self, secret_key="bot")

    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc server is ready.")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)


client = client(command_prefix=".", intents=discord.Intents.default())

# Get the amount of channel the bot is in
@client.ipc.route()
async def get_guild_count(data):
    return len(client.guilds)  # returns the len of the guilds to the client

# Get the guild(channel) id
@client.ipc.route()
async def get_guild_ids(data):
    final = []
    for guild in client.guilds:
        final.append(guild.id)
    return final  # returns the guild ids to the client

# Get guild(channel) info(data)
@client.ipc.route()
async def get_guild(data):
    guild = client.get_guild(data.guild_id)
    if guild is None: return None

    guild_data = {
        "name": guild.name,
        "id": guild.id,
        "prefix": "?"
    }

    return guild_data

# print out all users in the channel(guild) that is active(online status)
@client.command()
@commands.has_permissions(manage_messages=True)
async def members(ctx):
    members = ctx.guild.members

    for member in members:
        await ctx.send(member.name)
        print(member.name)
    await ctx.send("✅")

# Print I am ready when the bot is ready to be used
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over you"))
    print('I am ready.')


@client.command(aliases=['c'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)


@client.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=" No reason provided"):
    await member.send(f'You have been kicked from {ctx.message.guild.name}, because' + reason)
    await member.kick(reason=reason)


@client.command(aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=" No reason provided"):
    await ctx.send(member.name + f'has been banned from {ctx.message.guild.name}, because' + reason)
    await member.ban(reason=reason)


@client.command(aliases=['ub'])
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')

    for banned_entry in banned_users:
        user = banned_entry.user

        if (user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(member_name + " has been unbanned!")
            return
    await ctx.send(member + " was not found")

# Random number between 1 and 1000
@client.command()
async def randomNumber(ctx):
    ramndomnb = random.randint(1, 1000)
    await ctx.send(f'Your number is {ramndomnb}')


# Chooses a random post in the top category in the subreddit memes and posts it
@client.command()
async def meme(ctx, reddit_post="memes"):
    subreddit = reddit.subreddit(reddit_post)
    all_posts = []
    top = subreddit.top(limit=50)

    for posts in top:
        all_posts.append(posts)

    random_post = random.choice(all_posts)
    name = random_post.title
    url = random_post.url
    em = discord.Embed(title=name)
    em.set_image(url=url)
    await ctx.send(embed=em)


# Ping command shows the bots ping
@client.command()
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)}ms')


# Diceroll command (2 random numbers between 1 and 6
@client.command(aliases=['diceRoll', 'DiceRoll', 'dr'])
async def diceroll(ctx):
    roll = random.randint(1, 6)
    roll2 = random.randint(1, 6)
    await ctx.send(f'{ctx.author.name} rolled a {roll} and a {roll2}')


# Command for 8ball(different responses randomly choosen)
@client.command(aliases=['8ball'])
async def eightball(ctx, *, question):
    responses = ['As I see it, yes.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 'Don’t count on it.',
                 'It is certain.',
                 'It is decidedly so.',
                 'Most likely.',
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good.',
                 'Outlook good.',
                 'Reply hazy, try again.',
                 'Signs point to yes.',
                 'Very doubtful.',
                 'Without a doubt.',
                 'Yes.',
                 'Yes – definitely.',
                 'You may rely on it.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


# command to create a private room
@client.command()
async def createroom(ctx):
    guild = ctx.message.guild
    if guild is None:
        return

    # make a variable for category
    category = discord.utils.get(guild.categories, name="Game Rooms")

    # check if there is category "Game Rooms" if not make one
    if category is None:
        await ctx.guild.create_category("Game Rooms")
        category = discord.utils.get(guild.categories, name="Game Rooms")
    # make sure that atleast one other person is in the message
    if len(ctx.message.mentions) < 1:
        return

    # make a list for players
    playerIDs = []

    # add mentioned players in too the players list
    for mention in ctx.message.mentions:
        playerIDs.append(mention.id)

    # add author of the message to the players list
    playerIDs.append(ctx.author.id)

    players = []

    # check that players isnt in other game rooms already
    playersValid = True
    for pId in playerIDs:

        player = discord.utils.get(client.get_all_members(), id=pId)

        if not player:
            playersValid = False
            break

        for role in player.roles:
            if role.name[0:10] == "game-room-":
                playersValid = False
                break

        players.append(player)

    if playersValid == False:
        await ctx.send("Mentioned players were not valid")
        return

    channelName = ""
    validName = False

    # make a role for game room with a random number
    while validName == False:
        channelID = random.randint(1, 100)
        channelName = "game-room-" + str(channelID)

        for channel in guild.text_channels:
            if channelName != channel:
                validName = True
            else:
                validName = False

    print(f'Creating {channelName} channel...')

    role = channelName + "-player"
    authorizedRole = await guild.create_role(name=role, hoist=True)

    # declare perrmissions for the role, everyone can see in the game room but only those who have specifc role can write in it
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        authorizedRole: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    # make game room channel
    channel = await guild.create_text_channel(channelName, overwrites=overwrites, category=category)

    game_dict[channelName] = GameRoom(players, channelName)
    # add roles on players
    for player in players:
        await player.add_roles(authorizedRole)
    # make an embed(a type of message) that's send into the created game room channel with instructions
    MessageEmbed = discord.Embed(title=" Welcome to " + channelName + ".",color = discord.Colour.random())
    MessageEmbed.add_field(name="Here u can play few of our games", value="```Currently we have 2 games tick-tack-toe and SnakeEeyes. To play one of the games just write '!start snakeeyes' or '!start tictactoe'.```")
    print(f'{channelName} Created')
    await channel.send(embed=MessageEmbed)

# make command to delete room and the role
@client.command()
async def endroom(ctx):
    guild = ctx.message.guild

    channel = ctx.message.channel
    if channel.name[0:10] != "game-room-":
        return

    role_object = discord.utils.get(guild.roles, name=channel.name + "-player")

    await role_object.delete()

    await channel.delete()
    print(f'game room: {channel.name} Deleted')

    game_dict.pop(channel.name)


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.content.startswith('!'):
        room_instance = game_dict.get(message.channel.name)
        if room_instance is not None:
            output = room_instance.process_input(message)
            await message.channel.send(output)



@client.command()
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the stop command")
        return

    connected = ctx.author.voice
    if connected is None:
        await ctx.send("You need to be connected in a voice channel to use this command!")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice is None:
        await connected.channel.connect()

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
            voice.play(discord.FFmpegPCMAudio("song.mp3"))


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a channel")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("There is no audio playing")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


client.ipc.start()
client.run(TOKEN)
if __name__ == "__main__":
    app.run()
