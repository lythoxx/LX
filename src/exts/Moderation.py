from discord import (
    Color,
    Embed,
    Member,
    Interaction,
    app_commands,
    User
)
from discord.ext import commands
from discord.ui import (
    Select
)
from ui.ban.Ban import Ban
from ui.ban.Unban import Unban
from ui.misc.Kick import Kick
from ui.mute.Mute import Mute
from ui.mute.Unmute import Unmute
from ui.warn.Warn import Warn

from utils.Utils import Utils

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, interaction: Interaction, member: Member=None, reason: str=None):
        modal = Kick(title=f"Kick {member.name}#{member.discriminator}") if member is not None else Kick()
        modal.member_field.default = f"{member.name}#{member.discriminator}" if member is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self, interaction: Interaction, member: Member, *, reason: str=None):
        modal = Ban(title=f"Ban {member.name}#{member.discriminator}") if member is not None else Ban()
        modal.member_field.default = f"{member.name}#{member.discriminator}" if member is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self, interaction: Interaction, user: User=None, reason: str=None):
        modal = Unban(title=f"Unban {user.name}#{user.discriminator}") if user is not None else Unban()
        modal.user_field.default = f"{user.name}#{user.discriminator}" if user is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(mute_members=True)
    @app_commands.guild_only()
    async def mute(self, interaction: Interaction, member: Member=None, reason: str=None, modifier: str=None, duration: int=None):
        muted = Utils.open_file("src/json/muted.json")
        if member is not None and member in muted.keys() and muted[member.id][str(interaction.guild.id)] == str(interaction.guild.id):
            await interaction.response.send_message("User is alread muted", ephemeral=True)
        modal = Mute(title=f"Mute {member.name}#{member.discriminator}") if member is not None else Mute()
        modal.member_field.default = f"{member.name}#{member.discriminator}" if member is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        modal.time_modifier.default = modifier if modifier is not None else ""
        modal.duration.default = duration if duration is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(mute_members=True)
    @app_commands.guild_only()
    async def unmute(self, interaction: Interaction, member: Member=None, reason: str=None):
        muted = Utils.open_file("src/json/muted.json")
        if member is not None and member not in muted.keys():
            await interaction.response.send_message("Member is not muted", ephemeral=True)
        modal = Unmute(title=f"Unmute {member.name}#{member.discriminator}") if member is not None else Unmute()
        modal.member_field.default = f"{member.name}#{member.discriminator}" if member is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def warn(self, interaction: Interaction, member: Member=None, reason: str=None):
        modal = Warn(title=f"Warn {member.name}#{member.discriminator}") if member is not None else Warn()
        modal.member_field.default = f"{member.name}#{member.discriminator}" if member is not None else ""
        modal.reason_field.default = reason if reason is not None else ""
        await interaction.response.send_modal(modal)

    @app_commands.command()
    @commands.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unwarn(self, interaction: Interaction, member: Member, warn: int):
        warns = Utils.open_file("src/json/warns.json")
        if str(member.id) in warns.keys() and str(interaction.guild.id) in warns[str(member.id)].keys():
            reasons = warns[str(member.id)][str(interaction.guild.id)]
            try:
                reason = warns[str(member.id)][str(interaction.guild.id)][warn-1]
                warns[str(member.id)][str(interaction.guild.id)].pop(warn-1)
                if Utils.get_log_channel(interaction.guild.id):
                    await Utils.log(interaction.guild, f"**Removed Warning from {member.name}#{member.discriminator}**", reason, interaction.user, member, interaction.created_at)
                await interaction.response.send_message("Removed warning from user", ephemeral=True)
            except IndexError:
                await interaction.response.send_message("That warning does not exist", ephemeral=True)
        else:
            await interaction.response.send_message("That user does not have any warnings to remove", ephemeral=True)
        Utils.write_file("src/json/warns.json", warns)

    @app_commands.command()
    @commands.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def warns(self, interaction: Interaction, member: Member):
        warns = Utils.open_file("src/json/warns.json")
        if str(member.id) in warns.keys() and str(interaction.guild.id) in warns[str(member.id)].keys():
            reasons = warns[str(member.id)][str(interaction.guild.id)]
            reason = "`\n`"
            count = len(reasons)
            reason = reason.join(reasons)
            embed = Embed(description=f"Warns for {member.name}#{member.discriminator}", color=Color.red(), timestamp=interaction.created_at)
            embed.set_author(name=member, icon_url=member.avatar)
            embed.set_footer(text=f"Requested by: {interaction.user}")
            embed.add_field(name="Reason", value=f"`{reason}`", inline=True)
            embed.add_field(name="Count", value=count)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("This user doesn't have any warnings in this server", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation ext loaded")

async def setup(bot):
    await bot.add_cog(Moderation(bot))