from discord import (
    ButtonStyle,
    Interaction
)
from discord.ext import commands
from discord.ui import (
    Modal,
    TextInput,
    button,
    Button,
    View
)

import time

from utils.Utils import Utils

class Info(View):
    def __init__(self, error: int, duration: str, modifier: str):
        super().__init__()
        self.error = error
        self.duration = duration
        self.modifier = modifier

    @button(label="More Info", style=ButtonStyle.red)
    async def more_info(self, interaction: Interaction, button: Button):
        if self.error == 1 and self.modifier == "minutes":
            return await interaction.response.send_message(f"{self.duration} is not a valid value. The duration needs to be between 1 and 60", ephemeral=True)
        elif self.error == 1 and self.modifier == "hours":
            return await interaction.response.send_message(f"{self.duration} is not a valid value. The duration needs to be between 1 and 24", ephemeral=True)
        elif self.error == 1 and self.modifier == "days":
            return await interaction.response.send_message(f"{self.duration} is not a valid value. The duration needs to be between 1 and 7", ephemeral=True)
        elif self.error == 1 and not self.duration.isdigit():
            return await interaction.response.send_message(f"{self.duration} is not a valid value. The duration needs to be a whole number", ephemeral=True)
        elif self.error == 2:
            return await interaction.response.send_message(f"{self.modifier} is not a valid value. The time modifier needs to be minutes, hours or days", ephemeral=True)

class Mute(Modal, title="Mute"):
    member_field = TextInput(
        label="Member",
        placeholder="Member name AND discriminator or ID",
        required=True
    )

    reason_field = TextInput(
        label="Reason",
        placeholder="Reason for muting",
        required=True,
        max_length=50
    )

    time_modifier = TextInput(
        label="Time Modifier",
        placeholder="Time modifier (minutes, hours or days)",
        required=True,
        max_length=10
    )

    duration = TextInput(
        label="Duration",
        placeholder="Duration",
        required=True,
        max_length=2
    )

    def check_input(self):
        """
        Check if the input is valid.
        Error codes: 1 = invalid duration, 2 = invalid time modifier
        """
        # Check if the duration and time modifier are valid
        if str(self.time_modifier.value).lower().strip() == "minutes" or str(self.time_modifier.value).lower().strip() == "minute" or str(self.time_modifier.value).lower().strip() == "min" or str(self.time_modifier.value).lower().strip() == "m": # check if the time modifier is minutes
            modifier = "minutes"
            if self.duration.value.isdigit(): # check if the duration is a number
                if int(self.duration.value) > 0 and int(self.duration.value) <= 60:
                    return 0, int(self.duration.value) * 60, modifier # Everything is cool
                else:
                    return 1, self.duration.value, modifier # Duration is not a number between 1 and 60
            else:
                return 1, self.duration.value, modifier # Duration is not a number
        elif str(self.time_modifier.value).lower().strip() == "hours" or str(self.time_modifier.value).lower().strip() == "hour" or str(self.time_modifier.value).lower().strip() == "h": # check if the time modifier is hours
            modifier = "hours"
            if self.duration.value.isdigit(): # check if the duration is a number
                if int(self.duration.value) > 0 and int(self.duration.value) <= 24: # check if the duration is a number between 1 and 24
                    return 0, int(self.duration.value) * 3600, modifier
                else:
                    return 1, self.duration.value, modifier
            else:
                return 1, self.duration.value, modifier
        elif str(self.time_modifier.value).lower().strip() == "days" or str(self.time_modifier.value).lower().strip() == "day" or str(self.time_modifier.value).lower().strip() == "d": # check if the time modifier is days
            modifier = "days"
            if self.duration.value.isdigit(): # check if the duration is a number
                if int(self.duration.value) > 0 and int(self.duration.value) <= 7: # check if the duration is a number between 1 and 7
                    return 0, int(self.duration.value) * 3600 * 24, modifier
                else:
                    return 1, self.duration.value, modifier
            else:
                return 1, self.duration.value, modifier
        else:
            return 2, self.duration.value, self.time_modifier.value


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

        error, duration, modifier = self.check_input()
        if error != 0:
            await interaction.response.send_message("Invalid duration or time modifier", view=Info(error=error, duration=duration, modifier=modifier), ephemeral=True)
        else:
            try:
                await member.add_roles(guild.get_role(Utils.get_muted_role(str(guild.id))))
                await interaction.response.send_message(f"Muted {member.name} for {self.reason_field.value}.\nDuration: {self.duration.value} {modifier}", ephemeral=True)
                await member.send(f"You have been muted in {guild.id} for {self.reason_field.value}.\nDuration: {self.duration.value} {modifier}")
                muted = Utils.open_file("src/json/muted.json")
                if str(member.id) in muted.keys():
                    muted[str(member.id)].update({guild.id: round(time.time()) * 1000 + duration * 1000})
                else:
                    data = {member.id: {guild.id: round(time.time()) * 1000 + duration * 1000}}
                    muted.update(data)
                Utils.write_file("src/json/muted.json", muted)
                if Utils.get_log_channel(guild.id):
                    await Utils.log(guild, f"**Muted {member.name}#{member.discriminator}**", self.reason_field.value, interaction.user, member, interaction.created_at, f"{self.duration.value} {modifier}")
            except commands.RoleNotFound as rnf:
                await interaction.response.send_message(f"Could not mute {member.name}, because there is no role setup.", ephemeral=True)
            except FileNotFoundError as fnfe:
                await interaction.response.send_message("There has been an internal error. Please contact the developer to fix this problem", ephemeral=True)
