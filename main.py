import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

TOKEN = 'Token here'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load the opus library
discord.opus.load_opus('libopus.so.0')

@bot.command()
async def play(ctx, url: str):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.author.voice.channel.name)
    if not voice_channel:
        await ctx.send("You are not connected to a voice channel")
        return

    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

    with yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'noplaylist': True}) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            source = discord.FFmpegOpusAudio(filename)
        except Exception as e:
            await ctx.send(f"Error: {e}")
            return

    def after_play(error):
        os.remove(filename)

    voice_client.play(source, after=after_play)
    await ctx.send(f'Now playing: {info["title"]}')

@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Bot left the voice channel")
    else:
        await ctx.send("Bot is not connected to a voice channel")

@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused")
    else:
        await ctx.send("Nothing is playing")

@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed")
    else:
        await ctx.send("Nothing is paused")

bot.run(TOKEN)
