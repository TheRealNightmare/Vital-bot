import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

TOKEN = 'Discord Bot Token'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load the opus library
discord.opus.load_opus('libopus.so.0')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    voice_channel = discord.utils.get(bot.get_all_channels(), type=discord.VoiceChannel)
    if voice_channel:
        await voice_channel.connect()

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

@bot.command()
async def play(ctx, *, song: str):
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

    query = song

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
    ydl = yt_dlp.YoutubeDL(ydl_opts)

    try:
        if ".com" in song or "youtube.com" in song:
            # If it's a URL, directly use the URL to extract info
            info = ydl.extract_info(query, download=True)
        else:
            # If it's a search term, use 'ytsearch:' to search and extract info
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]

        filename = ydl.prepare_filename(info)
        source = discord.FFmpegOpusAudio(filename)

        # Now you can use 'source' to play the audio in your Discord voice channel
        # For example, if you have a voice client named 'vc':
        # vc.play(source)

    except Exception as e:
        await ctx.send(f"Error: {e}")
        return

    def after_play(error):
        os.remove(filename)
        if len(queue) > 0:
            next_song = queue.pop(0)
            bot.loop.create_task(play(ctx, song=next_song))  # Pass the song as a keyword argument

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        queue.append(song)
        await ctx.send(f'{song} added to the queue')
    else:
        voice_client.play(source, after=after_play)
        await ctx.send(f'Now playing: {info["title"]}')

queue = []

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song")
        if len(queue) > 0:
            next_song = queue.pop(0)
            bot.loop.create_task(play(ctx, next_song))
    else:
        await ctx.send("Nothing is currently playing")

@bot.event
async def on_voice_state_update(member, before, after):
    if bot.voice_clients:
        # Check if the bot is alone in the voice channel, then cleanup
        if len(bot.voice_clients[0].channel.members) == 1 and bot.user in bot.voice_clients[0].channel.members:
            await bot.voice_clients[0].disconnect()

bot.run(TOKEN)
