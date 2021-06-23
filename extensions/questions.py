from typing import Optional

from discord.ext import commands

import utils
from utils import contexts
from classes import MuffinCog, MuffinBot


class Questions(MuffinCog):
    category = "AI"
    
    def __init__(self, *args, **kwargs):
        super(Questions, self).__init__(*args, **kwargs)

        # Setup OpenAI API
        utils.setup_openai(self.bot.config.ai_config.api_key)

        print("Questions Module Loaded.")

    @commands.command(name="ask", aliases=["q"])
    async def ask(self, ctx: commands.Context, *, question: str):
        """Ask a question to the bot and it will provide an AI generated answer"""
        context = contexts.create_question_context(self.bot.config.data_path, question, self.bot.user.display_name)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send(result)

    @commands.command(name="complete")
    async def complete(self, ctx: commands.Context, *, text: str):
        """Send a text to bot and let it complete it using AI"""
        async with ctx.typing():
            result = await utils.create_completion_result(self.bot.loop, prompt=text, temperature=.8, max_tokens=64,
                                                          stop="\n", engine="davinci")
            await ctx.send(text + result)

    @commands.command(name="complete_long")
    async def complete_long(self, ctx: commands.Context, max_tokens: Optional[int] = 64, *, text: str):
        """Send a text and a number of max tokens to bot and let it complete the text"""
        async with ctx.typing():
            result = await utils.create_completion_result(self.bot.loop, prompt=text, temperature=.8,
                                                          max_tokens=max_tokens, stop="\n", engine="davinci")
            await ctx.send(text + result)

    @commands.command(name="instruct", alias=["instruction"])
    async def instruct(self, ctx: commands.Context, *, prompt: str):
        """Instruct AI to do a specific thing and watch the magic"""
        context = contexts.create_instruction_context(self.bot.config.data_path, instruction=prompt)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```"+result[:1993]+"```")

    @commands.command(name="instruct_custom")
    async def instruct_custom(self, ctx: commands.Context, max_tokens: Optional[int] = 64,
                              temperature: Optional[float] = 0.3, *, prompt: str):
        """Instruct AI to do a specific thing and watch the magic"""
        if 0 >= max_tokens > 256:
            return await ctx.send("Max tokens argument has to be between 0 and 256")
        context = contexts.create_instruction_context(self.bot.config.data_path, instruction=prompt)
        context.max_tokens, context.temperature = max_tokens, temperature
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```" + result[:1993] + "```")

    @commands.command(name="story")
    async def story(self, ctx: commands.Context, max_tokens: Optional[int] = 128, *, prompt: str):
        """Give an idea and let the AI write a story about it"""
        if 0 >= max_tokens > 256:
            return await ctx.send("Max tokens argument has to be between 0 and 256")
        context = contexts.create_story_context(self.bot.config.data_path, text=prompt)
        context.max_tokens = max_tokens
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```" + result[:1993] + "```")

    @commands.command(name="list")
    async def create_list(self, ctx: commands.Context, max_tokens: Optional[int] = 128,
                          temperature: Optional[float] = 1, *, prompt: str):
        """Give a prompt to create a list of items"""
        if 0 >= max_tokens > 256:
            return await ctx.send("Max tokens argument has to be between 0 and 256")
        context = contexts.create_list_context(self.bot.config.data_path, text=prompt)
        context.max_tokens, context.temperature = max_tokens, temperature
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```1." + result[:1991] + "```")

    @commands.command(name="translate")
    async def translate(self, ctx: commands.Context, *, text: str):
        """Translates any text to english using AI"""
        context = contexts.create_translation_context(self.bot.config.data_path, text=text)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send("```"+result[:1993]+"```")

    @commands.command(name="classify")
    async def classify(self, ctx: commands.Context, *, text: str):
        """Classifies the given text into following groups:
        0 - SFW
        1 - Sensitive
        2 - NSFW"""
        context = contexts.create_filter_context(self.bot.config.data_path, content=text)
        async with ctx.typing():
            result = await utils.create_completion_result_from_context(self.bot.loop, context)
            await ctx.send(str(result))


def setup(bot: MuffinBot):
    bot.add_cog(Questions(bot))
