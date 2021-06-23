import json
import os
from typing import Union, List
from dataclasses import dataclass


@dataclass
class AIContext:
    temperature: float
    stop: Union[str, List[str]]
    text: str
    max_tokens: int
    engine: str


def get_context(context_name, data_path) -> AIContext:
    with open(os.path.join(data_path, "contexts", f"{context_name}.json"), "r") as file:
        data = json.loads(file.read())
    return AIContext(
        data.get("temperature"),
        data.get("stop"),
        data.get("text"),
        data.get("max_tokens"),
        data.get("engine")
    )


def create_question_context(data_path: str, question: str, bot_name: str):
    context = get_context("helpbot", data_path)
    text = context.text + "\n\nQ: " + question.strip() + "\nA:"
    context.text = text.format(bot_name=bot_name)
    return context


def create_instruction_context(data_path: str, instruction: str):
    context = get_context("instruction", data_path)
    context.text = context.text.format(prompt=instruction.strip())
    return context


def create_story_context(data_path: str, text: str):
    context = get_context("write_story", data_path)
    context.text = context.text.format(prompt=text)
    return context


def create_list_context(data_path: str, text: str):
    context = get_context("write_list", data_path)
    context.text = context.text.format(prompt=text)
    return context


def create_translation_context(data_path: str, text: str):
    context = get_context("translator", data_path)
    context.text = context.text.format(prompt=text.strip())
    return context


def create_filter_context(data_path: str, content: str):
    context = get_context("content_classifier", data_path)
    context.text = context.text.format(content=content)
    return context

