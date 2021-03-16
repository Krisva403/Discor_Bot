import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name="over you"))
    print('I am ready.')


@client.command()
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)}ms')

@client.command()
async def diceRoll(ctx):
    roll = random.randint(1,6)
    await ctx.send(f'{ctx.author.name} rolled a {roll}')

client.run(TOKEN)