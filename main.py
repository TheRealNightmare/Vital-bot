from asyncio.tasks import wait
import discord
from discord import channel
from discord import guild
from discord.ext import commands
from discord.flags import Intents
import music


TOKEN = 'discord bot token'

client = commands.Bot(command_prefix='!')

cogs = [music]

for i in range(len(cogs)):
  cogs[i].setup(client)





@client.event
async def on_ready():
    print("The bot is now ready to use!!")


@client.command()
async def hello(ctx):
    username = str(ctx.author).split('#')[0]
    await ctx.send(f"hello!! {username} How can I help you")

@client.command()
async def goodbye(ctx):
    username = str(ctx.author).split('#')[0]
    await ctx.send(f"Goodbye {username} . Hope you have a good day")



client.run(TOKEN)