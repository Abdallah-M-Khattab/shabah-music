import discord
from discord.ext import commands
import wavelink
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)

# Lavalink Node info (عدل حسب إعداداتك)
LAVALINK_HOST = 'shabah-music-bot3-production.up.railway.app'  # internal host لو موجود
LAVALINK_PORT = 2333
LAVALINK_PASSWORD = 'youshallnotpass'  # نفس ما في application.yml
LAVALINK_REGION = 'europe'  # اختياري

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # إنشاء Node فقط إذا لم يكن موجود
    if not wavelink.NodePool.nodes:
        await wavelink.NodePool.create_node(
            bot=bot,
            host=LAVALINK_HOST,
            port=LAVALINK_PORT,
            password=LAVALINK_PASSWORD,
            region=LAVALINK_REGION
        )
        print('Lavalink Node created!')

# أمر الانضمام للقناة الصوتية
@bot.command()
async def join(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("أنت لست في أي قناة صوتية!")
    
    channel = ctx.author.voice.channel
    if not wavelink.NodePool.nodes:
        return await ctx.send("لا يوجد Node متصل بـ Lavalink حالياً.")
    
    player: wavelink.Player = await channel.connect(cls=wavelink.Player)
    await ctx.send(f"تم الانضمام إلى {channel.name}")

# أمر تشغيل الأغنية
@bot.command()
async def play(ctx, *, search: str = None):
    if not search:
        return await ctx.send("اكتب اسم الأغنية أو الرابط بعد الأمر!")
    
    if not ctx.voice_client:
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("أنت لست في أي قناة صوتية!")
        channel = ctx.author.voice.channel
        await channel.connect(cls=wavelink.Player)
    
    node = wavelink.NodePool.get_node()
    track = await wavelink.YouTubeTrack.search(search, return_first=True, node=node)
    
    if not track:
        return await ctx.send("لم أتمكن من إيجاد الأغنية.")
    
    await ctx.voice_client.play(track)
    await ctx.send(f"جاري تشغيل: **{track.title}**")

# أمر إيقاف الأغنية
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.stop()
        await ctx.send("تم إيقاف الأغنية.")
    else:
        await ctx.send("البوت ليس في أي قناة صوتية.")

# أمر مغادرة القناة
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("تم مغادرة القناة.")
    else:
        await ctx.send("البوت ليس في أي قناة صوتية.")

# أمر الإيقاف المؤقت
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.pause()
        await ctx.send("تم إيقاف الأغنية مؤقتاً.")
    else:
        await ctx.send("لا توجد أغنية تعمل حالياً.")

# أمر استكمال التشغيل
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        await ctx.voice_client.resume()
        await ctx.send("تم استكمال الأغنية.")
    else:
        await ctx.send("لا توجد أغنية موقوفة حالياً.")

# تشغيل البوت
TOKEN = os.getenv("DISCORD_TOKEN")  # تأكد أنك وضعت التوكن في Environment Variables
bot.run(TOKEN)
