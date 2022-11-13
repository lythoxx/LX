from datetime import datetime as dt

from exts.Help import Help

from discord import (
    Activity,
    ActivityType,
    AllowedMentions,
    Intents
)
from discord.ext import (
    commands,
    tasks
)
from json import load

import time

from utils.Utils import Utils

exts = [
    "Utility",
    "Moderation",
    "Events"
]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            activity=Activity(
                type=ActivityType.playing, name="/help | v2.1.0"
            ),
            allowed_mentions=AllowedMentions(everyone=False, users=True, roles=False, replied_user=False),
            case_insensitive=True,
            intents = Intents.all(),
            application_id=813713877740945468,
            command_prefix=None,
            help_command=Help()
        )

    async def on_message(self, message) -> None:
        pass

    @tasks.loop(seconds=30)
    async def check_muted(self):
        await self.wait_until_ready()
        muted = Utils.open_file("src/json/muted.json")
        current_time = round(time.time()) * 1000
        keys = list(muted.keys())
        for key in range(len(keys)):
            _id = keys[key]
            guilds = list(muted[_id].keys())
            for guild_key in range(len(guilds)):
                guild_id = guilds[guild_key]
                if muted[_id][guild_id] <= current_time:
                    guild = await self.fetch_guild(int(guild_id))
                    user = await guild.fetch_member(int(_id))
                    await user.remove_roles(guild.get_role(Utils.get_muted_role(guild.id)))
                    if Utils.get_log_channel(guild.id):
                        await Utils.log(guild, f"**Unmuted {user.name}#{user.discriminator}**", "Automatic unmute", self.user, user, dt.fromtimestamp(time.time()))
                    if len(guilds) == 1:
                        muted.pop(_id)
                    else:
                        muted[_id].pop(str(guild.id))
                    Utils.write_file("src/json/muted.json", muted)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        for ext in exts:
            await self.load_extension(f"exts.{ext}")

        self.check_muted.start()
        await self.tree.sync()


with open("src/json/token.json") as f:
    token = load(f)


if __name__ == "__main__":
    bot = Bot()
    bot.run(token["token"])