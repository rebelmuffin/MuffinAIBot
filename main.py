import discord
from discord.ext import commands

import utils
from classes import MuffinBot


bot = MuffinBot(config_filename="config.json")


@bot.check
async def globally_block_dms(ctx: commands.Context):
    """Globally blocks all DMs from everyone except the API bot owner"""
    app: discord.AppInfo = await bot.application_info()
    owner = app.owner
    if ctx.guild is None and ctx.author != owner:
        raise utils.NoDM
    return True

bot.run()
