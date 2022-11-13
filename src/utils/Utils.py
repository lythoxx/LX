from json import load, dump

import discord

class Utils:

    @staticmethod
    def open_file(file_name: str) -> dict:
        with open(file_name, "r") as f:
            return load(f)

    @staticmethod
    def write_file(file_name: str, data: dict) -> None:
        with open(file_name, "w") as f:
            dump(data, f, indent=4)

    @staticmethod
    def get_muted_role(guild: int) -> int:
        config = Utils.open_file("src/json/config.json")
        return int(config[str(guild)][0]) if config[str(guild)][0] is not None else None

    @staticmethod
    def get_log_channel(guild: int) -> int:
        config = Utils.open_file("src/json/config.json")
        return int(config[str(guild)][1]) if config[str(guild)][1] is not None else None

    @staticmethod
    async def log(guild: discord.Guild, description: str, reason: str, author: discord.Member, member: discord.Member, timestamp, duration: str=None, count: int=None):
        channel = Utils.get_log_channel(guild.id)
        channel = await guild.fetch_channel(channel)
        embed = discord.Embed(description=description, color=discord.Color.red(), timestamp=timestamp)
        embed.set_author(name=member, icon_url=member.avatar)
        embed.set_footer(text=f"Authorized by: {author}")
        embed.add_field(name="Reason", value=reason, inline=True)
        if duration != None:
            embed.add_field(name="Duration", value=duration)
        if count != None:
            embed.add_field(name="Count", value=count)
        await channel.send(embed=embed)
