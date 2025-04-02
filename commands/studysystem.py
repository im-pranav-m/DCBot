import discord
from discord.ext import commands
import os
import time
import aiohttp
import json
from datetime import datetime, timedelta
import asyncio

from datamanagement import update_database

from profilegenerator import generate

REGISTER_ROLE_ID = 1342852079923761214  # Role ID to assign

# Ensure the data folder exists
os.makedirs("data", exist_ok=True)

# File path

POMODORO_FILE = "data/pomodoro.json"

def load_pomodoro_data():
    """Loads Pomodoro data from the JSON file."""
    if not os.path.exists(POMODORO_FILE):
        return {}
    with open(POMODORO_FILE, "r") as f:
        return json.load(f)

def save_pomodoro_data(data):
    """Saves Pomodoro data to the JSON file."""
    with open(POMODORO_FILE, "w") as f:
        json.dump(data, f, indent=4)


def register(bot):
    #---------------------------------- COIN SYSTEM GET--------------------------------------------
    vc_sessions, stream_sessions, cam_sessions = {}, {}, {}
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        await asyncio.sleep(1)  # Small delay for accurate detection

        # Ignore bots
        if member.bot:
            return

        user_id, now = str(member.id), time.time()
        channel = bot.get_channel(1342785955857170493)

        # 🟢 User joins VC
        if before.channel is None and after.channel:
            vc_sessions[user_id] = now
        
        # 🔴 User leaves VC
        elif before.channel and after.channel is None:
            from datamanagement import isStreak
            streak = isStreak(userid=user_id)

            if user_id in vc_sessions:
                pomodoro_data = load_pomodoro_data()

                if user_id in pomodoro_data:
                    pomo_status = pomodoro_data[user_id].get("pomodoro_status")
                    notifi = pomodoro_data[user_id].get("pomodoro_notifications")

                    if pomo_status:
                        pomodoro_data[user_id]["pomodoro_status"] = False
                        save_pomodoro_data(pomodoro_data)

                        if notifi:
                            warn = "<:warning:1348205436435824754>"
                            disc = "<:disconnect:1348238302960029838>"
                            embed = discord.Embed(
                                title=f"{warn} Pomodoro Session Cancelled",
                                description=f"**Your Pomodoro session has been cancelled as you left the voice channel.**{disc}",
                                color=discord.Color.red()
                            )
                            embed.set_footer(text="Use '-pomonotification' to disable Pomodoro-based DMs.")

                            user = await bot.fetch_user(user_id)
                            await user.send(embed=embed)

                vc_duration = round((now - vc_sessions.pop(user_id)) / 60)
                earned_coins = round(vc_duration) * 2

                if channel:
                    print(f"📢 Sending message to {channel.name}")
                    await channel.send(f'{member.display_name} spent {vc_duration} minutes in VC.\nEarned {earned_coins} coins.')
                    update_database(member.id, member.name, round(vc_duration/60), earned_coins, vc_duration, 0, 0)
                else:
                    print("❌ Channel not found!")

            if user_id in stream_sessions:  # If streaming before leaving
                stream_duration = round((now - stream_sessions.pop(user_id)) / 60)
                if channel:
                    await channel.send(f'{member.name} streamed for {stream_duration} minutes in VC.')
                update_database(member.id, member.name, round(stream_duration/60), round(stream_duration * 2), 0, 0, stream_duration)
    
            if user_id in cam_sessions:  # If using cam before leaving
                cam_duration = round((now - cam_sessions.pop(user_id)) / 60)
                if channel:
                    await channel.send(f'{member.name} used camera for {cam_duration} minutes in VC.')
                update_database(member.id, member.name, round(cam_duration/60), round(cam_duration * 2), 0, cam_duration, 0) 
    
        # ▶️ User starts streaming
        if not before.self_stream and after.self_stream:
            stream_sessions[user_id] = now
    
        # ⏹️ User stops streaming
        elif before.self_stream and not after.self_stream:
            if user_id in stream_sessions:
                stream_duration = round((now - stream_sessions.pop(user_id)) / 60)
                if channel:
                    await channel.send(f'{member.name} streamed for {stream_duration} minutes in VC.')
                update_database(member.id, member.name, round(stream_duration/60), round(stream_duration * 2), 0, 0, stream_duration)
        
        # 📷 User turns on camera
        if not before.self_video and after.self_video:
            cam_sessions[user_id] = now
    
        # 🚫 User turns off camera
        elif before.self_video and not after.self_video:
            if user_id in cam_sessions:
                cam_duration = round((now - cam_sessions.pop(user_id)) / 60)
                if channel:
                    await channel.send(f'{member.name} used camera for {cam_duration} minutes in VC.')  
                update_database(member.id, member.name, round(cam_duration/60), round(cam_duration * 2), 0, cam_duration, 0)  

#--------------------------------------------------------------------------------------------------------




def profile(bot):
    @bot.slash_command(name="profile", description="Shows information about the profile",    integration_types={
        discord.IntegrationType.guild_install,
        discord.IntegrationType.user_install,
    })
    async def profile(ctx: discord.ApplicationContext, user: discord.Member = None):
        await ctx.defer()
        user = user or ctx.author  # Default to the command user if no one is mentioned
        username = user.name  # Get the username
        global_name = user.global_name
        avatar_url = user.display_avatar.url

        if user.bot:
            await ctx.respond("Definetly got better profile than yours 😏" , delete_after = 6)
            time.sleep(1)
            await ctx.respond("Tryna find bugs pookie? 🥰", ephemeral = True , delete_after = 5)
            return

        from datamanagement import get_user_vc,get_user_stream,get_user_cam,get_user_coins,get_user_xp,isStreak,streakdays
        coins = get_user_coins(user.id)
        xp = get_user_xp(user.id)
        vcmin = get_user_vc(user.id)
        cammin = get_user_cam(user.id)
        streammins = get_user_stream(user.id)
       

        strak = isStreak(user.id) 
        streakdays = streakdays(user.id)


        bar,bartxt = 75,"FAILURE"

        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    file_path = f"profilegeneration/{username}.png"  # Save as username.png
                    with open(file_path, "wb") as f:
                        f.write(await resp.read())
        #def generate(pfp , username , numcoins , numxp , vcmin , cammin, streamin, isstreak, streakdays,barpercentage,bartext)   
        generate(username,global_name,coins,xp,vcmin,cammin,streammins,strak,streakdays,bar,bartxt)
        
        banner_path = f"profilegeneration/{username}banner.png"
        if os.path.exists(banner_path):
            await ctx.respond(file=discord.File(banner_path))  # Send image
        else:
            await ctx.respond("Error generating banner ❌")

        os.remove(f"profilegeneration/{username}.png")  # Delete profile picture
        os.remove(banner_path)  

