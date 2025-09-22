import discord
from discord.ext import commands
import asyncio
import youtube_dl
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='-', intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

if not os.path.exists("downloads"):
    os.mkdir("downloads")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Joined {channel.name}')
    else:
        await ctx.send('You are not in a voice channel.')

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Left the voice channel.')
    else:
        await ctx.send('I am not in a voice channel.')

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not in a voice channel.")
            return

    voice_client = ctx.voice_client

    try:
        info = ytdl.extract_info(search, download=False)
        url = info['url']
    except Exception as e:
        await ctx.send("Could not find the video.")
        return

    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
    await ctx.send(f'Now playing: {info.get("title", "Unknown")}')

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the audio.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the audio.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Stopped the audio.")

bot.run(os.getenv('BOT_TOKEN'))
