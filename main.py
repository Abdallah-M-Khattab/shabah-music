import os
import discord
from discord.ext import commands
import wavelink

TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = os.environ.get("PREFIX", "-")

LAVALINK_HOST = os.environ.get("LAVALINK_HOSTNAME", "localhost")
LAVALINK_PORT = int(os.environ.get("LAVALINK_PORT", 2333))
LAVALINK_PASSWORD = os.environ.get("LAVALINK_PASSWORD", "youshallnotpass")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")

    node: wavelink.Node = wavelink.Node(
        uri="wss://shabah-music-bot3-production.up.railway.app",
        password="youshallnotpass"
    )
    await wavelink.NodePool.connect(client=bot, nodes=[node])




@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ You need to be in a voice channel.")
    channel = ctx.author.voice.channel
    await channel.connect(cls=wavelink.Player)
    await ctx.send(f"🔊 Joined {channel.name}")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.voice_client:
        return await ctx.send("❌ Bot is not in a voice channel.")
    
    player: wavelink.Player = ctx.voice_client
    track = await wavelink.YouTubeTrack.search(search, return_first=True)
    
    if not track:
        return await ctx.send(f"❌ No results found for: {search}")
    
    await player.play(track)
    await ctx.send(f"▶️ Now playing: **{track.title}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client:
        await ctx.voice_client.pause()
        await ctx.send("⏸ Paused.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client:
        await ctx.voice_client.resume()
        await ctx.send("▶️ Resumed.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        await ctx.voice_client.stop()
        await ctx.send("⏭ Skipped.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the channel.")

bot.run(TOKEN)







