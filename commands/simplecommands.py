import discord 

def simple_infos(bot):
    @bot.event
    async def on_member_join(member):
        await member.send(f"Welcome to the server, {member.mention}!!")

    @bot.slash_command(name="help_vc", description="Shows all available VC management commands")
    async def help_vc(ctx):
        embed = discord.Embed(
        title="📜 Voice Channel Management Commands",
        description="Here are the available VC management commands:",
        color=discord.Color.blue())
        
        embed.set_thumbnail(url=bot.user.display_avatar.url)

        embed.add_field(name="🔒 `/private`", value="Make your VC private (Only invited users can join).", inline=False)
        embed.add_field(name="🔓 `/public`", value="Make your VC public (Anyone can join).", inline=False)
        embed.add_field(name="✏️ `/renamevc <new name>`", value="Rename your custom VC.", inline=False)
        embed.add_field(name="📩 `/invite <@user>`", value="Invite a user to your private VC.", inline=False)
        embed.add_field(name="⚖️ `/kick <@user>`", value="Start a vote to kick a user from your VC.", inline=False)

        embed.set_footer(text="Use these commands to manage your VC effectively!")

        await ctx.respond(embed=embed)  # Only visible to the user