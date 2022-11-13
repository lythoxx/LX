from discord import (
    Interaction
)
from discord.ui import (
    Modal,
    TextInput
)

from utils.Utils import Utils

class Kick(Modal, title="Kick"):
    member_field = TextInput(
        label="Member",
        placeholder="Member name AND discriminator or ID",
        required=True
    )

    reason_field = TextInput(
        label="Reason",
        placeholder="Reason for kicking",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: Interaction):
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

        await interaction.response.send_message(f"kicked {member.name} for {self.reason_field.value}", ephemeral=True)
        await member.send(f"You have been kicked in {guild.name} for {self.reason_field.value}")
        await Utils.log(guild, f"**kicked {member.name}#{member.discriminator}**", self.reason_field.value, interaction.user, member, interaction.created_at)
        await member.kick(reason=self.reason_field.value)