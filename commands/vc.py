import discord
import asyncio


VC_CHANNEL_ID = 1339945156253712445
TEMP_VC_LOG_CHANNEL = 1342785955857170493
CATEGORY_ID_TO_CRATE_VC = 1339945241779769365


CHECK_INTERVAL = 3

joinlogs,deletelogs = True , True

def tempVC(bot):

    @bot.event
    async def on_voice_state_update(member, before, after):
        if after.channel and after.channel.id == VC_CHANNEL_ID and before.channel != after.channel:
            guild = member.guild
            category = discord.utils.get(guild.categories, id=CATEGORY_ID_TO_CRATE_VC)
    
            if category is None:
                print("❌ Error: Category not found! Check ID.")
                return
    
            # Create the voice channel
            new_vc = await guild.create_voice_channel(name=f"{member.name}'s VC", category=category)
            await member.move_to(new_vc)
    
            # Logging
            try:
                logchannel = bot.get_channel(TEMP_VC_LOG_CHANNEL) or await bot.fetch_channel(TEMP_VC_LOG_CHANNEL)
            except discord.NotFound:
                print("❌ Log channel not found!")
                logchannel = None
            if logchannel:
                await logchannel.send(f"🔊 || **{member.name}** has created a new VC. ✅")
    
        # Delete empty temp VCs
        if before.channel and before.channel.category and before.channel.category.id == CATEGORY_ID_TO_CRATE_VC:
            if len(before.channel.members) == 0:
                await asyncio.sleep(CHECK_INTERVAL)
                if len(before.channel.members) == 0:
                    await before.channel.delete()
    
                    logchannel = bot.get_channel(TEMP_VC_LOG_CHANNEL) or await bot.fetch_channel(TEMP_VC_LOG_CHANNEL)
                    if logchannel:
                        await logchannel.send(f"🗑️ || **{before.channel.name}** was deleted.")
    
    @bot.slash_command(name="renamevc", description="Rename your current VC")
    async def rename_vc(ctx, name: str):
        """Allows users to rename their temporary VC"""
        member = ctx.author
        if member.voice and member.voice.channel:
            vc = member.voice.channel
            if vc.category and vc.category.id == CATEGORY_ID_TO_CRATE_VC:  # Check if it's a temp VC
                await vc.edit(name=name)
                await ctx.respond(f"✏️ Renamed VC to **{name}**!", ephemeral=True)  # Ephemeral = visible only to user
            else:
                await ctx.respond("❌ You can only rename temporary VCs.", ephemeral=True)
        else:
            await ctx.respond("❌ You are not in a voice channel!", ephemeral=True)

    @bot.slash_command(name="private", description="Make your VC private")
    async def make_private(ctx):
        """Makes the VC private."""
        member = ctx.author
        if member.voice and member.voice.channel:
            vc = member.voice.channel

            # Remove @everyone's permission
            await vc.set_permissions(ctx.guild.default_role, connect=False)
            await vc.set_permissions(member, connect=True, manage_channels=True)  # Allow owner full control
            await ctx.respond("🔒 Your VC is now **private**!", ephemeral=True)
        else:
            await ctx.respond("❌ You are not in a voice channel!", ephemeral=True)

    @bot.slash_command(name="public", description="Make your VC public")
    async def make_public(ctx):
        """Makes the VC public."""
        member = ctx.author
        if member.voice and member.voice.channel:
            vc = member.voice.channel

            # Restore @everyone's permission
            await vc.set_permissions(ctx.guild.default_role, connect=True)
            await ctx.respond("🔓 Your VC is now **public**!", ephemeral=True)
        else:
            await ctx.respond("❌ You are not in a voice channel!", ephemeral=True)


    @bot.slash_command(name="invite", description="Invite a user to your voice channel")
    async def invite(ctx, user: discord.Member):
        """Invites a user to the voice channel and sends a stylish DM."""

        if user.bot:
            await ctx.respond("❌ Not a user!!", ephemeral = True)
            return

        member = ctx.author
        if member.voice and member.voice.channel:
            vc = member.voice.channel

            # Grant permission for the invited user to join the VC
            await vc.set_permissions(user, connect=True)

            # Create the clickable link
            vc_link = f"https://discord.com/channels/{ctx.guild.id}/{vc.id}"

            voice="<:voice:1347822668681973770>"
            bell = "<:bell:1347823129715802135>"
            chain = "<:chain:1347823530401599498>"

            # Enhanced Embed
            embed = discord.Embed(
                title=f"{voice} **Study Room Invitation!**",
                description=f"Hey {user.mention}! {bell}\n\n**{member.mention}** has invited you to join their study room.\nClick below to join the voice chat! 👇",
                color=discord.Color.blue()
            )
            embed.add_field(name=f"{chain} Join Now:", value=f"**[🔊 {vc.name}](<{vc_link}>)**", inline=False)

            # Add inviter's avatar as a thumbnail
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

            # Send the embed as a DM
            try:
                await user.send(embed=embed)
                await ctx.respond(f"✅ **{user.name}** has been invited! 📩", ephemeral=True)
            except discord.Forbidden:
                await ctx.respond(f"❌ Could not send a DM to **{user.name}**. They may have DMs disabled.", ephemeral=True)
        else:
            await ctx.respond("❌ You are not in a voice channel!", ephemeral=True)

#------------------------------------- KICKING STUFFFFFF -------------------------------------------------------------------------------
    vote_kick_sessions = {}

    @bot.slash_command(name="kick", description="Vote to kick a user from your voice channel")
    async def kick(ctx, target: discord.Member):
        """Start a vote to kick a user from the voice chat using reactions."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond("❌ You must be in a voice channel to use this command!", ephemeral=True)

        vc = ctx.author.voice.channel

        if target not in vc.members:
            return await ctx.respond(f"❌ {target.mention} is not in your voice channel!", ephemeral=True)

        if vc.id in vote_kick_sessions:
            return await ctx.respond("⚠️ A vote to kick is already in progress in this VC!", ephemeral=True)

        required_votes = (len(vc.members) // 2) + 1  # Majority needed
        vote_kick_sessions[vc.id] = {
            "target": target,
            "yes_votes": set(),
            "no_votes": set(),
            "required_votes": required_votes
        }

        embed = discord.Embed(
            title="🗳️ Vote Kick Started!",
            description=f"🚨 A vote to kick **{target.mention}** from **{vc.name}** has begun!",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🔹 How to Vote?", value="React ✅ to kick, ❌ to keep.", inline=False)
        embed.add_field(name="⚖️ Required Votes", value=f"**{required_votes}** votes needed", inline=False)
        embed.set_footer(text="Majority votes will remove the user from VC")

        msg = await ctx.respond(embed=embed)
        msg = await msg.original_response()

        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return (
                user in vc.members and 
                reaction.message.id == msg.id and 
                str(reaction.emoji) in ["✅", "❌"]
            )

        try:
            while True:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "✅":
                    vote_kick_sessions[vc.id]["no_votes"].discard(user)
                    vote_kick_sessions[vc.id]["yes_votes"].add(user)
                elif str(reaction.emoji) == "❌":
                    vote_kick_sessions[vc.id]["yes_votes"].discard(user)
                    vote_kick_sessions[vc.id]["no_votes"].add(user)

                yes_votes = len(vote_kick_sessions[vc.id]["yes_votes"])
                no_votes = len(vote_kick_sessions[vc.id]["no_votes"])

                # Update embed live
                embed.set_field_at(1, name="⚖️ Required Votes", value=f"**{yes_votes}/{required_votes}** votes needed", inline=False)
                await msg.edit(embed=embed)

                if yes_votes >= required_votes:
                    await target.move_to(None)  # Kick from VC
                    await vc.set_permissions(target, connect=False)
                    del vote_kick_sessions[vc.id]
                    embed.color = discord.Color.green()
                    embed.description = f"✅ **{target.mention} has been removed from {vc.name}!**"
                    await msg.edit(embed=embed)
                    return

        except asyncio.TimeoutError:
            del vote_kick_sessions[vc.id]
            embed.color = discord.Color.greyple()
            embed.description = f"⏳ **Vote expired!** No action was taken."
            await msg.edit(embed=embed)

