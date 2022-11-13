from discord import Interaction
from discord.ui import (
    Modal,
    TextInput
)

from utils.Utils import Utils

class Unmute(Modal, title="Unmute"):
    member_field = TextInput(
        label="Member",
        placeholder="Member name AND discriminator or ID",
        required=True
    )

    reason_field = TextInput(
        label="Reason",
        placeholder="Reason for unmuting",
        required=True
    )

    async def on_submit(self, interaction: Interaction) -> None:
        guild = interaction.guild
        try:
            member_id = int(self.member_field.value)
        except ValueError:
            member_id = 0
            try:
                member_name, member_discriminator = self.member_field.value.split('#')
            except ValueError:
                return await interaction.response.send_message("Invalid member name or ID")

        for _member in guild.members:
            if member_id != 0:
                if _member.id == member_id:
                    member = _member
                    break
            elif _member.name == member_name and _member.discriminator == member_discriminator:
                member = _member
                break
        else:
            return await interaction.response.send_message("Member not found.")

        try:
            await member.remove_roles(guild.get_role(Utils.get_muted_role(str(guild.id))))
            await interaction.response.send_message(f"Unmuted {member.name} for {self.reason_field.value}", ephemeral=True)
            muted = Utils.open_file("src/json/muted.json")
            muted.pop(str(member.id))
            Utils.write_file("src/json/muted.json", muted)
            if Utils.get_log_channel(guild.id):
                await Utils.log(guild, f"**Unmuted {member.name}#{member.discriminator}**", self.reason_field.value, interaction.user, member, interaction.created_at)
        except FileNotFoundError:
            await interaction.response.send_message("There has been an interal error. Please contact the developer to fix this problem.", ephemeral=True)