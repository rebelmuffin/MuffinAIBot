import json
from contextlib import suppress

from discord.ext import commands

import utils


def get_prompt(ctx: commands.Context) -> str:
    """Finds the prompt in invoked command"""
    prefix = ctx.prefix

    if not ctx.message.content.startswith(prefix):
        return ctx.message.content

    words = []

    # Make sure the words are not numbers
    for word in ctx.message.content.split(" "):
        if not word.isnumeric() and word:
            words.append(word)

    return " ".join(words)


async def is_owner(ctx: commands.Context):
    """Checks if the command author is bots API app owner"""
    app = await ctx.bot.application_info()
    owner = app.owner
    if ctx.author != owner:
        # Raise MissingPermissions exception for error handling reasons
        raise utils.OwnerOnly()
    return True


async def is_admin(ctx: commands.Context):
    """Checks if the command author is in guild admin list"""
    if ctx.guild is None:
        return True

    # Return true if author is bot owner
    with suppress(utils.OwnerOnly):
        return await is_owner(ctx)

    # Return true if author is a server administrator
    if ctx.author.guild_permissions.administrator:
        return True

    # Check guild info.json
    data_path = ctx.bot.get_guild_data_path(ctx.guild.id, "info.json")
    try:
        with open(data_path, "r") as file:
            data = json.loads(file.read())
    except FileNotFoundError:
        raise utils.AdminOnly()
    if ctx.author.id not in data.get("admins", []):
        raise utils.AdminOnly()
    return True


async def is_whitelisted(ctx: commands.Context):
    """Checks if the user was specified as admin in config"""
    # Return true if author is bot owner
    with suppress(utils.OwnerOnly):
        return await is_owner(ctx)

    # Check config for user's ID
    if ctx.author.id in ctx.bot.config.whitelist:
        print(f"User \"{ctx.author}\" authorized for `{ctx.command}` with message \"{ctx.message.content}\"")
        return True

    raise utils.WhitelistOnly()


async def is_appropriate(ctx: commands.Context):
    """Classifies the text using OpenAI classification endpoint and returns `True` if output is `0`"""
    # Return true if author is bot owner
    with suppress(utils.OwnerOnly):
        return await is_owner(ctx)

    # Find the prompt
    prompt = get_prompt(ctx)
    if not prompt:
        raise utils.TextInappropriate()

    # Classify the text
    classification = await utils.filter_text(ctx.bot, prompt)
    if classification in [1, 2]:
        raise utils.TextInappropriate()

    return True
