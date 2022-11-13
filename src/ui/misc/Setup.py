from discord import Interaction
from discord.ui import (
    Modal,
    TextInput
)

from utils.Utils import Utils

class Setup(Modal, title="Setup"):
    muted_role_field = TextInput(
        label = "Muted Role",
        placeholder = "The ID of the muted role",
        required = False
    )

    log_channel_field = TextInput(
        label = "Log Channel",
        placeholder = "The ID of the log channel",
        required = False
    )

    async def on_submit(self, interaction: Interaction) -> None:
        guild = interaction.guild
        config = Utils.open_file("src/json/config.json")
        if str(guild.id) in list(config.keys()):
            if self.muted_role_field.value == "" and self.log_channel_field.value == "":
                await interaction.response.send_message("Nothing has changed.")
            if self.muted_role_field.value != "" and self.log_channel_field.value == "":
                data = {guild.id: [self.muted_role_field.value, str(Utils.get_log_channel(guild.id))]}
                await interaction.response.send_message(f"Added `Muted Role` as `{self.muted_role_field.value}`")
            if self.muted_role_field.value == "" and self.log_channel_field.value != "":
                data = {guild.id: [str(Utils.get_muted_role(guild.id)), self.log_channel_field.value]}
                await interaction.response.send_message(f"Added `Log Channel` as `{self.log_channel_field.value}`")
            if self.muted_role_field.value != "" and self.log_channel_field.value != "":
                data = {guild.id: [self.muted_role_field.value, self.log_channel_field.value]}
                await interaction.response.send_message(f"Added `Muted Role` as `{self.muted_role_field.value}` and `Log Channel` as `{self.log_channel_field.value}`")
        else:
            if self.muted_role_field.value == "" and self.log_channel_field.value == "":
                await interaction.response.send_message("Nothing has changed.")
            if self.muted_role_field.value != "" and self.log_channel_field.value == "":
                data = {guild.id: [self.muted_role_field.value, None]}
                await interaction.response.send_message(f"Added `Muted Role` as `{self.muted_role_field.value}`")
            if self.muted_role_field.value == "" and self.log_channel_field.value != "":
                data = {guild.id: [None, self.log_channel_field.value]}
                await interaction.response.send_message(f"Added `Log Channel` as `{self.log_channel_field.value}`")
            if self.muted_role_field.value != "" and self.log_channel_field.value != "":
                data = {guild.id: [self.muted_role_field.value, self.log_channel_field.value]}
                await interaction.response.send_message(f"Added `Muted Role` as `{self.muted_role_field.value}` and `Log Channel` as `{self.log_channel_field.value}`")
        config.update(data)
        Utils.write_file("src/json/config.json", config)
