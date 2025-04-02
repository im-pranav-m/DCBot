import discord
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv

from commands.simplecommands import simple_infos
from commands.vc import tempVC
from commands.studysystem import register, profile
from commands.pomodoro import pomodoro, setup
from commands.music import MUSIC_BOTS, musicsystem

load_dotenv()  # Load environment variables

# ---------------------------- BOT 1 (General Commands Bot) ----------------------------
async def run_bot1():
    intents1 = discord.Intents.all()
    intents1.message_content = True  # Enable message content
    bot = commands.Bot(command_prefix="!", intents=intents1)  # Change to commands.Bot for compatibility

    @bot.event
    async def on_ready():
        print(f"{bot.user} (Bot 1) is ready and online!")

    # Load commands
    simple_infos(bot)
    register(bot)
    profile(bot)
    pomodoro(bot)
    setup(bot)

    await bot.start(os.getenv('TOKEN'))  # Start bot 1

# ---------------------------- BOT 2 (VC Bot) ----------------------------
async def run_bot2():
    intents2 = discord.Intents.all()
    intents2.voice_states = True  # Required for voice events
    vcbot = commands.Bot(command_prefix="!", intents=intents2)  # Change to commands.Bot

    @vcbot.event
    async def on_ready():
        print(f"{vcbot.user} (VC Bot) is ready and online!")

    tempVC(vcbot)
    musicsystem(vcbot)

    await vcbot.start(os.getenv('TOKEN2'))  # Start bot 2

# ---------------------------- MUSIC BOTS ----------------------------
async def music_bot(token_env, prefix, index):
    intents = discord.Intents.all()
    intents.message_content = True  # Ensure message content is enabled
    bot = commands.Bot(command_prefix=prefix, intents=intents)  # Change to commands.Bot

    @bot.event
    async def on_ready():
        print(f"{bot.user} is Ready and Online!")
        MUSIC_BOTS[index]["bot"] = bot  # Store bot reference

    await bot.start(os.getenv(token_env))

async def run_all_music_bots():
    await asyncio.gather(
        music_bot("MUSIC1", "*", 0),
        music_bot("MUSIC2", "?", 1),
        music_bot("MUSIC3", "#", 2),
        music_bot("MUSIC4", "$", 3),
        music_bot("MUSIC5", "%", 4)
    )

# ---------------------------- MAIN FUNCTION ----------------------------
async def main():
    await asyncio.gather(run_bot1(), run_bot2(), run_all_music_bots())

if __name__ == "__main__":
    asyncio.run(main())