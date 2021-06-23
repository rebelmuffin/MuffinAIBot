import math
import asyncio
from contextlib import suppress
from typing import Optional, Union, Tuple, List

import discord
from discord.ext import commands

from classes import MuffinBot, MuffinCog


class Category(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        # Create a set of categories
        categories = set()
        for _, cog in ctx.bot.cogs.items():
            if list(cog.walk_commands()):
                categories.add(cog.category)

        # Look through categories and find a match with given arguments
        for cat in categories:
            if cat.lower() == argument.lower():
                return cat
        raise commands.BadArgument("Category not found")


class Command(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        # Look through commands and find a matching qualified name
        command = ctx.bot.get_command(argument)
        if command is None:
            raise commands.BadArgument("Command not found")
        return command


class Help(MuffinCog):
    """Has help commands"""
    category = "misc"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_per_page = 5

    def _get_categories(self) -> List[str]:
        """Creates and returns a list of categories"""
        categories = set()
        for _, cog in self.bot.cogs.items():
            if list(cog.walk_commands()):
                categories.add(cog.category)
        return sorted(list(categories))

    def _generate_command_list(self, category: str, page_index: int) -> Tuple[discord.Embed, int]:
        """Creates and returns an embed with command list on given page of given category"""
        # Find the start and end index of command list depending on the page index
        list_start_index = page_index * self.commands_per_page
        list_end_index = list_start_index + self.commands_per_page

        # Create a command set
        command_set = set()
        for _, cog in self.bot.cogs.items():
            if cog.category == category:
                for cmd in list(cog.walk_commands()):
                    if not cmd.hidden:
                        command_set.add(cmd)

        # Get max page count
        page_count = math.ceil(len(command_set) / self.commands_per_page)

        # Ensure the page index is not more than or less than it should be
        if page_index >= page_count:
            page_index = page_count - 1
        if page_index <= 0:
            page_index = 0

        # Get the page relevant part of commands
        command_list = sorted(list(command_set), key=lambda c: c.qualified_name)[list_start_index:list_end_index]

        # Create embed
        embed = discord.Embed(title=f"{category.title()} Commands",
                              description=f"There are a total of `{len(command_set)}` commands in this category",
                              colour=discord.Colour.blurple())
        embed.set_footer(text=f"Page {page_index + 1}/{page_count}")
        for command in command_list:
            embed.add_field(name=command.qualified_name,
                            value=command.short_doc if command.short_doc else "No help message",
                            inline=False)
        return embed, page_count

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx: commands.Context, category: Optional[Category], *, command: Optional[Command]):
        """Provides information about command or category"""
        # Give basic info if no command or category was provided
        if category is None and command is None:
            embed = discord.Embed(title=self.bot.user.name,
                                  description=self.bot.description,
                                  colour=discord.Colour.blurple())
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"{ctx.prefix}{ctx.invoked_with} [command/category]")
            embed.add_field(name="Available Categories",
                            value='\n'.join([cat.title() for cat in self._get_categories()]),
                            inline=False)
            return await ctx.send(embed=embed)

        # Give information about the command if command was provided
        if command:
            command: Union[commands.Command, commands.Group]
            embed = discord.Embed(title=command.qualified_name,
                                  description=command.help,
                                  colour=discord.Colour.blurple())
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"{ctx.prefix}{ctx.invoked_with} [command/category]")

            # Show usage with signature
            embed.add_field(name="Usage", value=f"{ctx.prefix}{command.qualified_name} {command.signature}")

            # Show aliases if there are any
            if command.aliases:
                embed.add_field(name="Aliases", value=', '.join(f"`{a}`" for a in command.aliases), inline=False)

            # Show subcommands if command is a group
            if isinstance(command, commands.Group):
                embed.add_field(name="Subcommands", value=', '.join(f"`{c.qualified_name}`" for c in command.commands),
                                inline=False)
            return await ctx.send(embed=embed)

        # Give a list of commands in category if category was provided
        if category:
            category: str

            # Send the initial message
            current_page = 0
            embed, page_count = self._generate_command_list(category, current_page)
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
            sent_message = await ctx.send(embed=embed)

            # React to message and wait for reactions in a while loop if page count is more than 1
            if page_count > 1:
                while 1:
                    await sent_message.add_reaction("◀")
                    await sent_message.add_reaction("▶")
                    await sent_message.add_reaction("⏺")

                    # Wait for the reactions
                    try:
                        def check(r, u):
                            return u == ctx.author and r.emoji in ["◀", "▶", "⏺"] and r.message == sent_message
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                    # Handle timeout
                    except asyncio.TimeoutError:
                        try:
                            await sent_message.clear_reactions()
                        except discord.Forbidden:
                            await sent_message.remove_reaction("◀", self.bot.user)
                            await sent_message.remove_reaction("▶", self.bot.user)
                            await sent_message.remove_reaction("⏺", self.bot.user)
                        break

                    # Remove the new reaction for clarity
                    with suppress(discord.Forbidden):
                        await reaction.remove(user)

                    # Pin the message
                    if reaction.emoji == "⏺":
                        try:
                            await sent_message.clear_reactions()
                        except discord.Forbidden:
                            await sent_message.remove_reaction("◀", self.bot.user)
                            await sent_message.remove_reaction("▶", self.bot.user)
                            await sent_message.remove_reaction("⏺", self.bot.user)
                        break

                    # Go to previous page
                    if reaction.emoji == "◀":
                        if current_page < 1:
                            continue
                        current_page -= 1
                        embed, _ = self._generate_command_list(category, current_page)
                        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
                        await sent_message.edit(embed=embed)

                    # Go to next page
                    if reaction.emoji == "▶":
                        if current_page+1 >= page_count:
                            continue
                        current_page += 1
                        embed, _ = self._generate_command_list(category, current_page)
                        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
                        await sent_message.edit(embed=embed)


def setup(bot: MuffinBot):
    bot.add_cog(Help(bot))
