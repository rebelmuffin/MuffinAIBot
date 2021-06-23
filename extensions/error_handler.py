import asyncio

import openai
import discord
from discord.ext import commands

from utils import raise_failure
from classes import MuffinBot, MuffinCog


class ErrorHandler(MuffinCog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Global error handler. Should only work if the error is not handled by the command itself."""
        if isinstance(error, commands.MissingPermissions):
            await raise_failure(ctx.message.channel, f"You lack the permission to do this {ctx.author.mention}!")
        elif isinstance(error, commands.BotMissingPermissions):
            await raise_failure(ctx.message.channel, f"I lack the permission to do this!")
        elif isinstance(error, commands.MissingRole):
            await raise_failure(ctx.message.channel, f"You need `{error.missing_role.name}` role to use this command")
        elif isinstance(error, commands.BotMissingRole):
            await raise_failure(ctx.message.channel, f"I need `{error.missing_role.name}` role to use this command")
        elif isinstance(error, commands.NSFWChannelRequired):
            await raise_failure(ctx.message.channel, "This command can only be used in a NSFW channel")
        elif isinstance(error, commands.CheckFailure):
            await raise_failure(ctx.message.channel, str(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            await raise_failure(ctx.message.channel, f"You need to provide a `{error.param.name}` parameter")
        elif isinstance(error, commands.TooManyArguments):
            await raise_failure(ctx.message.channel, f"You provided too many arguments!")
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await raise_failure(ctx.message.channel, f"Expected closing quote...")
        elif isinstance(error, commands.InvalidEndOfQuotedStringError):
            await raise_failure(ctx.message.channel, f"Expected a space after the closing quote...")
        elif isinstance(error, commands.UnexpectedQuoteError):
            await raise_failure(ctx.message.channel, f"Unexpected quote...")
        elif isinstance(error, commands.ArgumentParsingError):
            await raise_failure(ctx.message.channel, "Failed to parse the arguments")
        elif isinstance(error, commands.CheckFailure):
            await raise_failure(ctx.message.channel, f"You are not qualified to use this command {ctx.author.mention}")
        elif isinstance(error, commands.CommandOnCooldown):
            await raise_failure(ctx.message.channel, f"You have to wait `{int(error.retry_after)}` seconds to use this command")
        elif isinstance(error, commands.BadArgument):
            await raise_failure(ctx.message.channel, str(error))
        elif isinstance(error, commands.BadUnionArgument):
            await raise_failure(ctx.message.channel, "Couldn't find what you were looking for")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.Forbidden):
                await raise_failure(ctx.message.channel, f"I lack the permission to do this!")
            elif isinstance(error.original, asyncio.TimeoutError):
                await ctx.send("Too late!")
            elif isinstance(error.original, openai.error.APIConnectionError):
                await raise_failure(ctx.message.channel, error.original.user_message)
            else:
                raise error.original
        else:
            raise error


def setup(bot: MuffinBot):
    bot.add_cog(ErrorHandler(bot))
