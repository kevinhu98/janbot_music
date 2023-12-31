#taken from https://github.com/eric-yeung/Discord-Bot
import discord
import os
# load our local env so we dont have the token in public
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from yt_dlp import YoutubeDL

load_dotenv()
client = commands.Bot(command_prefix='.', intents=discord.Intents.all())  # prefix our commands with '.'

players = {}

@client.event  # check if bot is ready
async def on_ready():
    print('Bot online')


# command for bot to join the channel of the user, if the bot has already joined and is in a different channel, it will move to the channel the user is in
@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


# command to play sound from a youtube URL
@client.command()
async def play(ctx, *url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    #voice = get(client.voice_clients, guild=ctx.guild)
    
    # make sure voice is connected , todo: change to join func
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            url = " ".join(url)
            # case if url is a link 
            if "https://www.youtube.com" in url:
                info = ydl.extract_info(url, download=False)
                URL = info['url']
                title = info['title']
            # case if url is keywords
            else:
                info = ydl.extract_info("ytsearch:{url}".format(url=url), download=False)
                URL = info['entries'][0]['url']
                title = info['entries'][0]['title']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Janbot is playing {title}'.format(title=title))

# check if the bot is already playing
    else:
        await ctx.send("Bot is already playing")
        return


# command to resume voice if it is paused
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


# command to pause voice if it is playing
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send('Music stopped')


# command to clear channel messages
@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Messages have been cleared")

@client.command()
async def leave(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    await ctx.send("Janbot has been purged")

client.run(os.getenv('TOKEN'))