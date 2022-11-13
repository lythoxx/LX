from discord import (
    Interaction
)
from discord.ui import (
    Modal,
    TextInput
)

from utils.Utils import Utils

class Unban(Modal, title="Unban"):
    user_field = TextInput(
        label="User",
        placeholder="User name AND discriminator or ID",
        required=True
    )

    reason_field = TextInput(
        label="Reason",
        placeholder="Reason for unbanning",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        try:
            user_id = int(self.user_field.value)
        except ValueError:
            user_id = 0
            try:
                user_name, user_discriminator = self.user_field.value.split('#')
            except ValueError:
                return await interaction.response.send_message("Invalid user name or ID")

        async for ban_entry in guild.bans():
            _user = ban_entry.user
            if user_id != 0:
                if _user.id == user_id:
                    user = _user
                    break
            elif _user.name == user_name and _user.discriminator == user_discriminator:
                user = _user
                break
        else:
            return await interaction.response.send_message("User not found.")

        await interaction.response.send_message(f"Unbanned {user.name} for {self.reason_field.value}", ephemeral=True)
        await Utils.log(guild, f"**Unbanned {user.name}#{user.discriminator}**", self.reason_field.value, interaction.user, user, interaction.created_at)
        await guild.unban(user, reason=self.reason_field.value)