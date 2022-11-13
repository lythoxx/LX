from discord import app_commands, Interaction
from discord.ext import commands
from discord.ui import Modal

from ui.misc.Setup import Setup

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def setup(self, interaction: Interaction):
        modal: Modal = Setup()
        await interaction.response.send_modal(modal)


    @commands.Cog.listener()
    async def on_ready(self):
        print("Utility ext Loaded")


async def setup(bot):
    await bot.add_cog(Utility(bot))