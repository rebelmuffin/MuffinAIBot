from asyncio import BaseEventLoop
from typing import Union, List

import openai

from utils import contexts


def setup_openai(api_key: str):
    openai.api_key = api_key


def sync_create_completion(prompt: str, temperature: float,
                           max_tokens: int, stop: Union[str, List[str]], engine="davinci") -> openai.Completion:
    """Creates completion using OpenAI API"""
    return openai.Completion.create(engine=engine, prompt=prompt, temperature=temperature, max_tokens=max_tokens,
                                    stop=stop)


async def create_completion(loop: BaseEventLoop, prompt: str, temperature: float,
                            max_tokens: int, stop: Union[str, List[str]], engine="davinci") -> openai.Completion:
    """Asynchronously creates completion using OpenAI API"""
    return await loop.run_in_executor(None, sync_create_completion, prompt, temperature, max_tokens, stop, engine)


async def create_completion_result(loop: BaseEventLoop, prompt: str, temperature: float,
                                   max_tokens: int, stop: Union[str, List[str]], engine="davinci") -> str:
    """Asynchronously creates completion using OpenAI API and only returns the result text"""
    result = await create_completion(loop, prompt, temperature, max_tokens, stop, engine)
    return result["choices"][0]["text"]


async def create_completion_from_context(loop: BaseEventLoop, context: contexts.AIContext):
    """Asynchronously creates completion from given `AIContext`"""
    result = await create_completion(loop, context.text, context.temperature, context.max_tokens, context.stop,
                                     context.engine)
    return result


async def create_completion_result_from_context(loop: BaseEventLoop, context: contexts.AIContext):
    """Asynchronously creates completion from given `AIContext` and only returns the resulting text"""
    result = await create_completion_from_context(loop, context)
    return result["choices"][0]["text"]
