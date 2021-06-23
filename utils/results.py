from typing import Union

from contextlib import suppress

import discord


async def raise_failure(channel: Union[discord.TextChannel, discord.DMChannel], text: str):
    """Sends an embed notifying failure

    :param channel: Channel to sen the embed to
    :param text: Text to use in embed description

    :returns bool: If the message was sent or not
    """
    embed = discord.Embed(title=None, description=text, colour=discord.Colour.red())
    with suppress(discord.HTTPException, discord.Forbidden):
        await channel.send(embed=embed)
        return True
    return False


async def raise_success(channel: Union[discord.TextChannel, discord.DMChannel], text: str):
    """Sends an embed notifying success

        :param channel: Channel to sen the embed to
        :param text: Text to use in embed description

        :returns bool: If the message was sent or not
        """
    embed = discord.Embed(title=None, description=text, colour=discord.Colour.green())
    with suppress(discord.HTTPException, discord.Forbidden):
        await channel.send(embed=embed)
        return True
    return False
