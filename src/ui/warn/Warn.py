from discord import (
    Interaction
)
from discord.ui import (
    Modal,
    TextInput
)

import time

from utils.Utils import Utils

class Warn(Modal, title="Warn"):
    member_field = TextInput(
        label="Member",
        placeholder="Member name AND discriminator or ID",
        required=True
    )

    reason_field = TextInput(
        label="Reason",
        placeholder="Reason for warning",
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


        warns = Utils.open_file("src/json/warns.json")
        count = 1
        reason = self.reason_field.value
        member_str = str(member.id)
        guild_str = str(guild.id)
        reason = self.reason_field.value
        if member_str in warns.keys():
            if guild_str in warns[member_str].keys():
                count = len(warns[member_str][guild_str])
                if count == 3:
                    await interaction.response.send_message(f"Banned {member.name} for having been warned 3 times", ephemeral=True)
                    await member.send(f"You have been banned in {guild.name} for having been warned 3 times.")
                    if Utils.get_log_channel(guild.id):
                        await Utils.log(guild, f"**Banned {member.name}#{member.discriminator}**", "Warned 3 times", interaction.user, member, interaction.created_at)
                    await member.ban(reason="Warned 3 times")
                    warns[member_str].pop(guild_str) if len(warns[member_str].keys()) > 1 else warns.pop(member_str)
                else:
                    warns[member_str][guild_str].append(reason)
                    count = len(warns[member_str][guild_str])
            else:
                warns[member_str].update({guild_str: [reason]})
                count = len(warns[member_str][guild_str])
        else:
            warns.update({member_str: {guild_str: [reason]}})
        await interaction.response.send_message(f"Warned {member.name} for {self.reason_field.value}", ephemeral=True)
        if Utils.get_log_channel(guild.id):
            await Utils.log(guild, f"**Warned {member.name}#{member.discriminator}**", self.reason_field.value, interaction.user, member, interaction.created_at, count=count)
        await member.send(f"You have been warned in {guild.name} for {self.reason_field.value}")
        Utils.write_file("src/json/warns.json", warns)