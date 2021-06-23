import time
import pkg_resources
import asyncio
import textwrap
import io
import sys
from datetime import datetime
from contextlib import suppress

import psutil
import discord
from discord.ext import commands

from utils import checks
from classes import MuffinBot, MuffinCog


def format_code(py_code, prefix, command):
    if py_code.lower().startswith(f"{prefix}{command}"):
        py_code = py_code[6:]
    if py_code.startswith("\n"):
        py_code = py_code[1:]
    if py_code.startswith("```"):
        py_code = py_code[3:]
    if py_code.startswith("py\n"):
        py_code = py_code[3:]
    if py_code.endswith("```"):
        py_code = py_code[:-3]
    if py_code.startswith("``"):
        py_code = py_code[2:]
    if py_code.endswith("``"):
        py_code = py_code[:-2]

    return py_code


async def checkexists(msg):
    channel = msg.channel
    try:
        await channel.fetch_message(msg.id)
        return True
    except discord.NotFound:
        return False


async def exec_async(code, context=None):
    code = code.rstrip()

    if not code:
        return ''

    if not context:
        context = {}
        context.update(globals())

    def exec_print(value, *args, sep=' ', end='\n', flush=False, file=None):
        nonlocal exec_out
        nonlocal std_print
        file = exec_out if not file else file
        std_print(value, *args, sep=sep, end=end, flush=flush, file=file)

    std_print = print
    exec_out = io.StringIO()
    context['print'] = exec_print

    exec(f'async def exec_func():\n{textwrap.indent(code, "    ")}', context)
    await context['exec_func']()

    return exec_out.getvalue()


async def try_exec_async(code, ctx, context=None, message=None):
    try:
        if not message:
            message = await ctx.send("Executing...")
        else:
            await message.edit(content='Executing...')

        future = asyncio.ensure_future(exec_async(code, context))
        result = await future

        with suppress(Exception):
            await ctx.message.add_reaction("✅")

        await message.edit(content=f"```py\n{result if result else None}\n```")
    except SyntaxError as se:
        if se.text is None:
            await message.edit(content=f"```py\n{se.__class__.__name__} {se}\n```")
        await message.edit(content=f"```py\nSyntaxError: {se.text} {'^':>{se.offset}}\n{type(se).__name__}: {se}\n```")
    except Exception as ex:
        await message.edit(content=f"```py\nException: {ex}\n```")

    return message


class Debug(MuffinCog):
    category = "debug"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = psutil.Process()
        self.cureval = []

    @commands.command(hidden=True)
    async def shutdown(self, ctx: commands.Context):
        await ctx.send("This is unfai-")
        await self.bot.logout()
        await self.bot.close()
        await self.bot.loop.close()

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Measures latency between discord servers and bot server"""
        before = time.monotonic()
        msg = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        heartbeat = int(self.bot.latency * 1000)
        await msg.edit(content=f":ping_pong: Pong! Took: `{int(ping)}ms` (Heartbeat: `{heartbeat}ms`)")

    @commands.check(checks.is_owner)
    @commands.command(aliases=["stats"])
    async def status(self, ctx: commands.Context):
        """Gives information about bot's status"""
        # Measure ping first
        before = time.monotonic()
        msg = await ctx.send("Working...")
        ping = int((time.monotonic() - before) * 1000)
        heartbeat = int(self.bot.latency * 1000)

        # Create the embed
        emb = discord.Embed(title="Bot Status", description=f"Latency: `{ping}ms`\nHeartbeat: `{heartbeat}ms`",
                            colour=discord.Colour.blurple())
        # Get statistics
        total_members = 0
        total_online = 0
        offline = discord.Status.offline
        for member in self.bot.get_all_members():
            total_members += 1
            if member.status is not offline:
                total_online += 1

        total_unique = len(self.bot.users)

        text_channels = 0
        voice_channels = 0
        total_guilds = 0
        for guild in self.bot.guilds:
            total_guilds += 1
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text_channels += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice_channels += 1
        emb.add_field(
            name="Members", value=f"`{total_members}` total\n`{total_unique}` unique\n`{total_online}` unique online")
        emb.add_field(
            name="Channels",
            value=f"`{text_channels + voice_channels}` total\n`{text_channels}` text\n`{voice_channels}` voice")
        emb.add_field(name="Guilds", value=f"`{total_guilds}`")

        # Get memory and CPU usage
        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        emb.add_field(
            name="Process", value=f"Memory Usage: `{memory_usage:.2f} MiB`\nCPU Usage: `{cpu_usage:.2f}%`",
            inline=False)

        # Add other information
        version = pkg_resources.get_distribution('discord.py').version
        emb.set_footer(text=f"discord.py v{version}")
        emb.timestamp = datetime.utcnow()
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        await msg.edit(embed=emb, content=None)

    @commands.check(checks.is_owner)
    @commands.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, *, extension: str):
        """Reloads the extension. Only usable by owners"""
        if f"extensions.{extension}" not in self.bot.extensions:
            return await ctx.send("Unknown cog")
        sent_message = await ctx.send(f"Reloading `{extension}`")
        try:
            self.bot.reload_extension(f"extensions.{extension}")
        except Exception as e:
            return await ctx.send(f"Error occurred: `{e}`")
        await sent_message.edit(content=f"Successfully reloaded `{extension}`")

    @commands.check(checks.is_owner)
    @commands.command(aliases=["exec", "e"])
    async def eval(self, ctx: commands.Context, *, py_code: str):
        """Executes given python code. Only usable by owners"""
        if py_code is not None:
            py_code = format_code(py_code, ctx.prefix, ctx.invoked_with)
            message = None
            context = {
                "bot": self.bot,
                "ctx": ctx,
                "message": ctx.message,
                "channel": ctx.channel,
                "author": ctx.author,
                "guild": ctx.guild,
                "discord": discord
            }

            with suppress(Exception):
                while True:
                    context.update(globals())
                    message = await try_exec_async(py_code, ctx, context, message)

                    if not message:
                        break

                    if not (await checkexists(ctx.message)):
                        await message.delete()
                        return

                    _, after = await self.bot.wait_for(
                        "message_edit",
                        timeout=60,
                        check=lambda b, a: True if a.id == ctx.message.id else False
                    )

                    if not (await checkexists(ctx.message)):
                        await message.delete()
                        return

                    await ctx.message.remove_reaction("✅", member=self.bot.user)
                    py_code = format_code(after.content, ctx.prefix, ctx.invoked_with)

            with suppress(Exception):
                if not (await checkexists(ctx.message)):
                    await message.delete()
                    return


def setup(bot: MuffinBot):
    bot.add_cog(Debug(bot))
