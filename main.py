import discord
from discord.ext import commands
import wavelink
import asyncio
import os

# ===== إعداد التوكن والبادئة =====
TOKEN = os.environ.get("TOKEN")  # تأكد من وضع التوكن في متغير البيئة
PREFIX = "-"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ===== حدث عند جاهزية البوت =====
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    # الاتصال بـ Lavalink Node فقط إذا لم يكن متصل
    if not wavelink.NodePool.nodes:
        node = wavelink.Node(
            uri="wss://shabah-music-bot3-production.up.railway.app:2333", 
            password="youshallnotpass",
            region="europe"
        )
        await wavelink.NodePool.connect(client=bot, nodes=[node])
        print("Lavalink node connected.")

# ===== أمر الانضمام للقناة الصوتية =====
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ You must be in a voice channel!")
    if not wavelink.NodePool.nodes:
        return await ctx.send("❌ Lavalink node is not connected yet.")
    
    channel = ctx.author.voice.channel
    await channel.connect(cls=wavelink.Player)
    await ctx.send(f"✅ Connected to **{channel.name}**")

# ===== أمر الخروج من القناة الصوتية =====
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Disconnected.")
    else:
        await ctx.send("❌ I'm not in a voice channel.")

# ===== أمر تشغيل الأغاني =====
@bot.command()
async def play(ctx, *, search: str = None):
    if not search:
        return await ctx.send("❌ You need to provide a song name or URL!")

    if not ctx.voice_client:
        # إذا لم يكن البوت في قناة، انضم تلقائياً
        if ctx.author.voice:
            await join(ctx)
        else:
            return await ctx.send("❌ You must be in a voice channel!")

    player: wavelink.Player = ctx.voice_client

    # البحث عن الأغنية على يوتيوب
    try:
        track = await wavelink.YouTubeTrack.search(search, return_first=True)
    except Exception as e:
        return await ctx.send(f"❌ Error searching track: {e}")

    if not track:
        return await ctx.send("❌ No results found.")

    await player.play(track)
    await ctx.send(f"🎶 Now playing: **{track.title}**")

# ===== أمر إيقاف الأغنية =====
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped playback.")
    else:
        await ctx.send("❌ Nothing is playing.")

# ===== أمر مؤقت للتخطي =====
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped current track.")
    else:
        await ctx.send("❌ Nothing is playing.")

# ===== تشغيل البوت =====
bot.run(TOKEN)
