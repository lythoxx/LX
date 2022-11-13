import discord
from discord.ext import commands

class Help(commands.MinimalHelpCommand):
    def __init__(self) -> None:
        super().__init__(command_attrs={
            "help": "Show help for this bot"
        })

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        page = 0
        cogs = bot.cogs  # get all of your cogs
        cogs.sort()

        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author

        embed = await self.bot_help_paginator(page, cogs)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                        '\N{BLACK LEFT-POINTING TRIANGLE}',
                        '\N{BLACK RIGHT-POINTING TRIANGLE}',
                        '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                        '\N{BLACK SQUARE FOR STOP}',
                        '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except TimeoutError:  # session has timed out
                try:
                    await help_embed.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction 
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = 0
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -1:  # check whether to go to the final page
                        page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == len(cogs):  # check whether to go to the first page
                        page = 0
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    all_cogs = '`, `'.join([cog for cog in cogs])
                    embed = discord.Embed(title=f'Help with {bot.user.name}\'s commands', description=bot.description,
                                            color=discord.Colour.purple())
                    embed.add_field(
                        name=f'Currently there are {len(cogs)} cogs loaded, which includes (`{all_cogs}`) :gear:',
                        value='`<...>` indicates a required argument,\n`[...]` indicates an optional argument.\n\n'
                                '**Don\'t however type these around your argument**')
                    embed.add_field(name='What do the emojis do:',
                                    value=':track_previous: Goes to the first page\n'
                                            ':track_next: Goes to the last page\n'
                                            ':arrow_backward: Goes to the previous page\n'
                                            ':arrow_forward: Goes to the next page\n'
                                            ':stop_button: Deletes and closes this message\n'
                                            ':information_source: Shows this message')
                    embed.set_author(name=f'You were on page {page + 1}/{len(cogs)} before',
                                        icon_url=ctx.author.avatar_url)
                    embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                                        icon_url=ctx.bot.user.avatar_url)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break

    async def bot_help_paginator_reactor(self, message, reactions):
            for reaction in reactions:
                await message.add_reaction(reaction)

    async def bot_help_paginator(self, page: int, cogs):
        ctx = self.context
        bot = ctx.bot
        all_commands = [command for command in await self.filter_commands(bot.commands)]  # filter the commands the user can use
        cog = bot.get_cog(cogs[page])  # get the current cog

        embed = discord.Embed(title=f'Help with {cog.qualified_name} ({len(all_commands)} commands)',
                            description=cog.description, color=discord.Colour.blurple())
        embed.set_author(name=f'We are currently on page {page + 1}/{len(cogs)}', icon_url=ctx.author.avatar_url)
        for c in cog.walk_commands():
            if await c.can_run(ctx) and not c.hidden:
                signature = self.get_command_signature(c)
                description = self.get_command_description(c)
                if c.parent:  # it is a sub-command
                    embed.add_field(name=f'**╚╡**{signature}', value=description)
                else:
                    embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                        icon_url=ctx.bot.user.avatar_url)
        return embed

    def get_command_aliases(self, command):  # this is a custom written method along with all the others below this
        """Method to return a commands aliases"""
        if not command.aliases:  # check if it has any aliases
            return ''
        else:
            return f'command aliases are [`{"` | `".join([alias for alias in command.aliases])}`]'

    def get_command_description(self, command):
        """Method to return a commands short doc/brief"""
        if not command.short_doc:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc

    def get_command_help(self, command):
        """Method to return a commands full description/doc string"""
        if not command.help:  # check if it has any brief or doc string
            return 'There is no documentation for this command currently'
        else:
            return command.help
