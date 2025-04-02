import discord
import os
import asyncio

MUSIC_BOTS = [
    {"token": os.getenv("MUSIC1"), "bot": None},
    {"token": os.getenv("MUSIC2"), "bot": None},
    {"token": os.getenv("MUSIC3"), "bot": None},
    {"token": os.getenv("MUSIC4"), "bot": None},
    {"token": os.getenv("MUSIC5"), "bot": None},
]
available_bots = []


async def auto_disconnect(bot, voice_client, check_interval=30):
    while True:
        await asyncio.sleep(check_interval)
        if not voice_client.is_connected():
            break
        if len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
            print(f"Disconnected {bot.user.name} from {voice_client.channel.name} due to inactivity.")
            for music_bot in MUSIC_BOTS:
                if music_bot["bot"] == bot:
                    available_bots.append((MUSIC_BOTS.index(music_bot) + 1, bot))
                    break
            break


async def join_vc(bot, user_channel_id):
    global available_bots
    channel = bot.get_channel(user_channel_id)
    if channel:
        voice_client = await channel.connect()
        bot.voice_clients.append(voice_client)
        available_bots = [(num, b) for num, b in available_bots if b != bot]
        bot.loop.create_task(auto_disconnect(bot, voice_client))


def musicsystem(bot):
    music = discord.SlashCommandGroup("music", "Music bot commands")

    @music.command(name="connect", description="Make a music bot join VC")
    async def connect(ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You must be in a voice channel to use this command!")
            return
        user_channel = ctx.author.voice.channel
        global available_bots
        for music_bot in MUSIC_BOTS:
            if music_bot["bot"] and music_bot["bot"].voice_clients:
                for vc in music_bot["bot"].voice_clients:
                    if vc.channel.id == user_channel.id:
                        await ctx.respond("A bot is already in this VC.")
                        return
        available_bots = [
            (i + 1, music_bot["bot"])
            for i, music_bot in enumerate(MUSIC_BOTS)
            if music_bot["bot"] and not music_bot["bot"].voice_clients
        ]
        print("Available Bots:", [bot[0] for bot in available_bots])
        if not available_bots:
            await ctx.respond("No available music bots at the moment.")
            return
        bot_number, music_bot = available_bots[0]
        user_channel_id = user_channel.id
        if music_bot:
            await join_vc(music_bot, user_channel_id)
            await ctx.respond(f"Music bot {bot_number} has joined VC!")
        else:
            await ctx.respond(f"Music bot {bot_number} is not online.")

    @music.command(name="disconnect", description="Disconnect the music bot from your VC")
    async def disconnect(ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You must be in a voice channel to use this command!")
            return
        user_channel = ctx.author.voice.channel
        for music_bot in MUSIC_BOTS:
            if music_bot["bot"] and music_bot["bot"].voice_clients:
                for vc in music_bot["bot"].voice_clients:
                    if vc.channel.id == user_channel.id:
                        await vc.disconnect()
                        await ctx.respond("Disconnected the music bot from your VC.")
                        return
        await ctx.respond("No music bot is in your VC.")

    bot.add_application_command(music)

