from typing import Optional
from datetime import datetime, timedelta

from discord.ext import commands

import utils
from utils import contexts, checks
from classes import MuffinCog, MuffinBot


class Questions(MuffinCog):
    category = "AI"
    
    def __init__(self, *args, **kwargs):
        super(Questions, self).__init__(*args, **kwargs)

        # Setup OpenAI API
        utils.setup_openai(self.bot.config.ai_config.api_key)

        # Per-user invocation time dict and config for cooldowns
        self.enable_cooldown = True
        self.cooldown = 120
        self.invocation_times = {}

        print("Questions Module Loaded.")

    async def check_cooldown(self, ctx: commands.context):
        """Checks the user command cooldown in context"""
        if not self.enable_cooldown:
            return True

        now = datetime.utcnow()

        # Exclude bot owner from all cooldowns
        if await checks.is_owner(ctx):
            return True

        # Return if author never been in cooldown before
        last_time: datetime = self.invocation_times.get(ctx.author.id, None)
        if not last_time:
            self.invocation_times[ctx.author.id] = now
            return True

        cooldown_end = last_time + timedelta(seconds=self.cooldown)

        # Return if time has passed since cooldown end
        if cooldown_end < now:
            self.invocation_times[ctx.author.id] = now
            return True

        retry_after = (cooldown_end - now).total_seconds()
        print((cooldown_end - now))

        raise commands.CommandOnCooldown(None, retry_after)

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="ask", aliases=["q"])
    async def ask(self, ctx: commands.Context, *, question: str):
        """Ask a question to the bot and it will provide an AI generated answer"""
        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create question context and contact API
        context = contexts.create_question_context(self.bot.config.data_path, question, self.bot.user.display_name)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send(result)

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="complete")
    async def complete(self, ctx: commands.Context, *, text: str):
        """Send a text to bot and let it complete it using AI"""
        # Check for cooldown
        await self.check_cooldown(ctx)

        # Send the text to API without a context
        async with ctx.typing():
            result = await utils.create_completion_result(self.bot.loop, prompt=text, temperature=.8, max_tokens=64,
                                                          stop="\n", engine="davinci")
            await ctx.send(text + result)

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="complete_long")
    async def complete_long(self, ctx: commands.Context, max_tokens: Optional[int] = 64, *, text: str):
        """Send a text and a number of max tokens to bot and let it complete the text"""
        # Check for cooldown
        await self.check_cooldown(ctx)

        # Send the text to API without a context
        async with ctx.typing():
            result = await utils.create_completion_result(self.bot.loop, prompt=text, temperature=.8,
                                                          max_tokens=max_tokens, stop="\n", engine="davinci")
            await ctx.send(text + result)

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="instruct", alias=["instruction"])
    async def instruct(self, ctx: commands.Context, *, prompt: str):
        """Instruct AI to do a specific thing and watch the magic"""
        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create instruction context and contact API
        context = contexts.create_instruction_context(self.bot.config.data_path, instruction=prompt)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```"+result[:1993]+"```")

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="instruct_custom")
    async def instruct_custom(self, ctx: commands.Context, max_tokens: Optional[int] = 64,
                              temperature: Optional[float] = 0.3, *, prompt: str):
        """Instruct AI to do a specific thing and watch the magic"""
        # Limit tokens
        if 0 >= max_tokens > 256:
            return await utils.raise_failure(ctx.channel, "Max tokens argument has to be between 0 and 256")

        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create instruction context and contact API
        context = contexts.create_instruction_context(self.bot.config.data_path, instruction=prompt)
        # Set custom `max_tokens` and `temperature`
        context.max_tokens, context.temperature = max_tokens, temperature
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```" + result[:1993] + "```")

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="story")
    async def story(self, ctx: commands.Context, max_tokens: Optional[int] = 256, *, prompt: str):
        """Give an idea and let the AI write a story about it"""
        # Limit tokens
        if 0 >= max_tokens > 512:
            return await utils.raise_failure(ctx.channel, "Max tokens argument has to be between 0 and 256")

        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create a new story context and contact API
        context = contexts.create_story_context(self.bot.config.data_path, text=prompt)
        # Set custom `max_tokens`
        context.max_tokens = max_tokens
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```" + result[:1993] + "```")

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="list")
    async def create_list(self, ctx: commands.Context, max_tokens: Optional[int] = 128,
                          temperature: Optional[float] = 1, *, prompt: str):
        """Give a prompt to create a list of items"""
        # Limit tokens
        if 0 >= max_tokens > 256:
            return await ctx.send("Max tokens argument has to be between 0 and 256")

        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create new list context and contact API
        context = contexts.create_list_context(self.bot.config.data_path, text=prompt)
        # Set custom `max_tokens` and `temperature`
        context.max_tokens, context.temperature = max_tokens, temperature
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```1." + result[:1991] + "```")

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="translate")
    async def translate(self, ctx: commands.Context, *, text: str):
        """Translates any text to english using AI"""
        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create new translation context and contact API
        context = contexts.create_translation_context(self.bot.config.data_path, text=text)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```"+result[:1993]+"```")

    @commands.check(checks.is_whitelisted)
    @commands.check(checks.is_appropriate)
    @commands.command(name="classify")
    async def classify(self, ctx: commands.Context, *, text: str):
        """Classifies the given text into following groups:
        0 - SFW
        1 - Sensitive
        2 - NSFW"""

        # Check for cooldown
        await self.check_cooldown(ctx)

        # Create new classification context and contact API
        context = contexts.create_filter_context(self.bot.config.data_path, content=text)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send(str(result))


def setup(bot: MuffinBot):
    bot.add_cog(Questions(bot))
