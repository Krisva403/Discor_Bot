import os
import discord
import random
import youtube_dl
import praw
from games.GameRoom import GameRoom
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

reddit = praw.Reddit(client_id="JSEQrmvt-zdUJg",
                     client_secret="XSa7-69NIBQUuA710spi4UNcZ36OGQ",
                     username="BlindPick0",
                     password="BlindPick0",
                     user_agent="BlindPick", check_for_async=False)

game_dict = {}


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


@client.command()
async def randomNumber(ctx):
    ramndomnb = random.randint(1, 1000)
    await ctx.send(f'Your number is {ramndomnb}')


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


@client.command()
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)}ms')


@client.command(aliases=['diceRoll', 'DiceRoll', 'dr'])
async def diceroll(ctx):
    roll = random.randint(1, 6)
    roll2 = random.randint(1, 6)
    await ctx.send(f'{ctx.author.name} rolled a {roll} and a {roll2}')


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


@client.command()
async def createroom(ctx):
    guild = ctx.message.guild
    if guild is None:
        return

    category = discord.utils.get(guild.categories, name="Game Rooms")

    if category is None:
        await ctx.guild.create_category("Game Rooms")
        category = discord.utils.get(guild.categories, name="Game Rooms")

    if len(ctx.message.mentions) < 1:
        return

    playerIDs = []
    for mention in ctx.message.mentions:
        playerIDs.append(mention.id)

    playerIDs.append(ctx.author.id)

    players = []

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

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        authorizedRole: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    channel = await guild.create_text_channel(channelName, overwrites=overwrites, category=category)

    game_dict[channelName] = GameRoom(players, channelName)

    for player in players:
        await player.add_roles(authorizedRole)

    print(f'{channelName} Created')


@client.command()
async def endgame(ctx):
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


client.run(TOKEN)
