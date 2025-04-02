import discord
from discord.ext import commands
import json
import os

SUBJECTS_FILE = "data/subjects.json"

def load_subjects():
    """Loads subjects from the JSON file, creating a new one if it doesn't exist."""
    if not os.path.exists(SUBJECTS_FILE):
        with open(SUBJECTS_FILE, "w") as f:
            json.dump({}, f, indent=4)
    with open(SUBJECTS_FILE, "r") as f:
        return json.load(f)

def save_subjects(data):
    """Saves subjects to the JSON file."""
    with open(SUBJECTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

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


rocket = "<:rocket:1348200487396048966>"
class ConfirmView(discord.ui.View):
    """Confirmation buttons for starting the Pomodoro session, restricted to the original user."""
    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author  # Store the original user who initiated the interaction.

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensures only the original author can interact with the buttons."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ You cannot interact with this!", ephemeral=True)
            return False
        return True
    
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary, custom_id="pomodoro_yes")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Handles the 'Yes' button click."""   
        user_id = str(interaction.user.id)  # Convert to string for JSON keys
        pomodoro_data = load_pomodoro_data()   
        # If user is not in JSON, create a new entry
        if user_id not in pomodoro_data:
            pomodoro_data[user_id] = {"pomodoro_status": True, "pomodoro_notifications": True}
        else:
            # If user exists, update only the required fields
            pomodoro_data[user_id]["pomodoro_status"] = True
            pomodoro_data[user_id]["pomodoro_notifications"] = True   
        save_pomodoro_data(pomodoro_data)
        print(f"Updated Pomodoro Data: {pomodoro_data}")  # Debugging   
        
        await interaction.response.send_message(f"{rocket} Pomodoro session started!", ephemeral=True)
        self.disable_all_items()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, custom_id="pomodoro_no")
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Handles the 'No' button click by updating the embed."""
        embed = interaction.message.embeds[0]
        embed.title = "❌ Pomodoro Cancelled"
        embed.description = f"{interaction.user.mention} has cancelled the session."
        embed.clear_fields()  # Remove old fields
        embed.color = discord.Color.dark_gray()

        self.disable_all_items()
        await interaction.message.edit(embed=embed, view=self, delete_after=5)


class SubjectDropdown(discord.ui.Select):
    """Dropdown for selecting a subject."""
    def __init__(self, user_id):
        subjects_data = load_subjects()
        subjects = subjects_data.get(str(user_id), [])

        options = [
            discord.SelectOption(label=subj, value=subj)
            for subj in subjects
        ] if subjects else [discord.SelectOption(label="No subjects available", value="None", default=True)]

        super().__init__(placeholder="Select a subject...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """Handles the dropdown selection."""
        selected_subject = self.values[0]

        if selected_subject == "None":
            await interaction.response.send_message("❌ No subjects available to select.", ephemeral=True)
            return

        # Directly show the Pomodoro modal after selection
        modal = PomodoroModal(selected_subject)
        await interaction.response.send_modal(modal)


class SubjectView(discord.ui.View):
    """View for selecting a subject."""
    def __init__(self, user_id):
        super().__init__()
        self.selected_subject = None
        self.add_item(SubjectDropdown(user_id))


class PomodoroModal(discord.ui.Modal):
    """Modal for inputting Pomodoro session details."""
    def __init__(self, selected_subject: str):
        super().__init__(title="🍅 Create a Pomodoro Session")
        self.selected_subject = selected_subject

        self.add_item(discord.ui.InputText(label="Study Duration (Minutes)", placeholder="25", required=True))
        self.add_item(discord.ui.InputText(label="Short Break Duration (Minutes)", placeholder="5", required=True))
        self.add_item(discord.ui.InputText(label="Long Break Duration (Minutes)", placeholder="15", required=True))
        self.add_item(discord.ui.InputText(label="Long Break After (Sessions)", placeholder="4", required=True))

    async def callback(self, interaction: discord.Interaction):
        """Handles the modal submission."""
        study_time = int(self.children[0].value)
        short_break = int(self.children[1].value)
        long_break = int(self.children[2].value)
        long_break_after = int(self.children[3].value)

        total_sessions = long_break_after - 1
        estimated_time = (study_time + short_break) * total_sessions + study_time + long_break
        formatted_time = f"{estimated_time // 60:02}:{estimated_time % 60:02}:00"

        tomato = "<:tomato:1344164360284803143>"
        hourglass = "<:hourglass:1344167916488364094>"
        breaks = "<:break:1344168607017603224>"
        chill = "<:chill:1344168903462486129>"
        duration = "<:duration:1344169186628341842>"
        coin = "<:dollar:1343920175581495318>"
        book = "<:books:1348200848324562944>"

        embed = discord.Embed(
            title=f"{tomato} Pomodoro",
            description="**Confirm the action?**",
            color=discord.Color.red()
        )
        embed.add_field(name=f"{hourglass} Study", value=f"```{study_time} min```", inline=True)
        embed.add_field(name=f"{breaks} Short Break", value=f"```{short_break} min```", inline=True)
        embed.add_field(name=f"{chill} Long Break", value=f"```{long_break} min```", inline=True)
        embed.add_field(name=f"{coin} Rewards", value=f"```{study_time * long_break_after}```", inline=True)
        embed.add_field(name=f"{duration} Estimated Duration", value=f"```{formatted_time}```", inline=True)
        embed.add_field(name=f"{book} Subject", value=f"```{self.selected_subject}```", inline=True)

        await interaction.response.send_message(embed=embed, view=ConfirmView(interaction.user))


class Subjects(commands.Cog):
    """Cog for managing subjects."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pomonotification")
    async def subcommand(self, ctx, action1: str = None):
        user_id = str(ctx.author.id)
        pomodata = load_pomodoro_data()
        enb = "<:active:1348243836664811560>"
        dsb = "<:disabled:1348244101484777503>"
        wrn="<:warning_orange:1348248675083747449>"
        if action1 is None:
            embed = discord.Embed(
                title="Pomodoro Notifications",
                description=f"{enb} Use `-pomonotification on` to enable notifications\n"
                            f"{dsb} Use `-pomonotification off` to disable notifications",
                color=discord.Color.blue()
            )
            await ctx.reply(embed=embed)

        elif action1.lower() == "on":
            pomodata[user_id]["pomodoro_notifications"] = True
            save_pomodoro_data(pomodata)
            embed = discord.Embed(
                title="✅ Pomodoro Notifications Enabled",
                description=f"{enb} Pomodoro Notifications have been enabled.",
                color=discord.Color.green()
            )
            await ctx.reply(embed=embed)

        elif action1.lower() == "off":
            pomodata[user_id]["pomodoro_notifications"] = False
            save_pomodoro_data(pomodata)
            embed = discord.Embed(
                title="❌ Pomodoro Notifications Disabled",
                description=f"{dsb} Pomodoro Notifications have been disabled.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(
                title=f"{wrn} Invalid Command",
                description="Command not detected! Use `-pomonotification on/off`.",
                color=discord.Color.orange()
            )
            await ctx.reply(embed=embed)
        

    @commands.command(name="sub")
    async def sub_command(self, ctx, action: str = None, *, subject: str = None):
        """Manage subjects using -sub, -sub add {subject}, or -sub del {subject/index}."""
        user_id = str(ctx.author.id)
        subjects_data = load_subjects()

        # Ensure user has a record in the JSON
        if user_id not in subjects_data:
            subjects_data[user_id] = []

        if action is None:
            # Display subjects
            subjects = subjects_data[user_id]
            folder = "<:folder:1348201158161989722>"
            embed = discord.Embed(
                title=f"{folder} Your Subjects",
                color=discord.Color.blue()
            )

            if not subjects:
                folder = "<:folder:1348201158161989722>"
                embed.description = f"{folder} No subjects set yet!"
            else:
                subject_list = "\n".join([f"**{i+1}.** {s}" for i, s in enumerate(subjects)])
                embed.description = subject_list

            await ctx.reply(embed=embed)

        elif action.lower() == "add" and subject:
            # Add a subject
            if subject in subjects_data[user_id]:
                embed = discord.Embed(
                    description=f"⚠️ Subject **{subject}** already exists!",
                    color=discord.Color.red()
                )
                await ctx.reply(embed=embed)
                return

            subjects_data[user_id].append(subject)
            save_subjects(subjects_data)

            embed = discord.Embed(
                description=f"✅ **{subject}** has been added to your subjects!",
                color=discord.Color.green()
            )
            await ctx.reply(embed=embed)

        elif action.lower() == "del" and subject:
            # Delete subject by name or index
            try:
                subjects = subjects_data[user_id]
                if subject.isdigit():  # Check if the input is a number (index)
                    index = int(subject) - 1
                    if 0 <= index < len(subjects):
                        removed_subject = subjects.pop(index)
                        save_subjects(subjects_data)

                        embed = discord.Embed(
                            description=f"🗑️ Removed **{removed_subject}** from your subjects!",
                            color=discord.Color.orange()
                        )
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.reply(embed=discord.Embed(description="❌ Invalid subject index!", color=discord.Color.red()))
                else:  # Remove by subject name
                    if subject in subjects:
                        subjects.remove(subject)
                        save_subjects(subjects_data)

                        embed = discord.Embed(
                            description=f"🗑️ Removed **{subject}** from your subjects!",
                            color=discord.Color.orange()
                        )
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.reply(embed=discord.Embed(description=f"❌ Subject **{subject}** not found!", color=discord.Color.red()))
            except Exception as e:
                await ctx.reply(embed=discord.Embed(description=f"⚠️ Error: {str(e)}", color=discord.Color.red()))

        else:
            embed = discord.Embed(
                description="⚠️ Invalid command usage!\nUse `-sub`, `-sub add {subject}`, or `-sub del {subject/index}`.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)


def pomodoro(bot):

    @bot.slash_command(name="pomodoro", description="Create a Pomodoro session")
    async def pomodoro(ctx: discord.ApplicationContext):
        """Slash command to create a Pomodoro session, only if the user is in a voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            warn="<:warning:1348205436435824754>"
            await ctx.respond(f"{warn} You must be in a voice channel to use this command!", ephemeral=True)
            return

        view = SubjectView(ctx.author.id)
        book = "<:books:1348200848324562944>"
        await ctx.respond(f"{book} Select a subject for your Pomodoro session:", view=view, ephemeral=True,delete_after=8)


def setup(bot):
    """Adds the Subjects cog to the bot."""
    bot.add_cog(Subjects(bot))