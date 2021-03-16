
#Discord Bot
import os
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GENERAL_CH = int(os.getenv('GENERAL_CHANNEL'))

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
	guild = discord.utils.get(client.guilds, name=GUILD)

	print(
		f'{client.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

	members = '\n - '.join([member.name for member in guild.members])
	print(f'Guild Members:\n - {members}')

@client.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel_send(f'Hi {member.name}, welcome to my Discord server!')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	randomReplies = [
		'💯',
		(
			'Cool story, '
			'Bro.'
		),
	]

	if message.content == "1!":
		response = random.choice(randomReplies)
		await message.channel.send(response)

# Auto Kick
@tasks.loop(hours=48)
async def called_once_a_day():
	guild = discord.utils.get(client.guilds, name=GUILD)
	channel = client.get_channel(GENERAL_CH)

	agent_role = discord.utils.get(guild.roles, name="Secret Agent")
	regular_role = discord.utils.get(guild.roles, name="Temporary Visa")
	if agent_role is None or regular_role is None:
		print('One or more of the roles are not found!')
		return
	empty = True
	for member in guild.members:
		if agent_role not in member.roles:
			if regular_role not in member.roles:
				print(f'Spy without visa - {member.name}')
				empty = False

				await channel.send("{} visa has expired".format(member.mention))
				await member.kick(reason="Visa Expired")
			else:
				print(f'Spy exposed - {member.name}')
				empty = False
		# if member.name == "Benyte":
		# 	await channel.send("{} visa has expired".format(member.mention))
		# 	await member.kick(reason="Visa Expired")
	if empty:
		print('No spies were found this time')

@called_once_a_day.before_loop
async def before():
	await client.wait_until_ready()
	print("Bot is ready...")

called_once_a_day.start()

client.run(TOKEN)