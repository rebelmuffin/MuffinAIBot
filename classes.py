import json
import pathlib
import os
from typing import List, Union
from dataclasses import dataclass

import discord
from discord.ext import commands

import utils


@dataclass
class AIConfig:
    api_key: str
    dm_respond: bool


@dataclass
class BotConfig:
    token: str
    intents: List[str]
    data_path: str
    command_prefix: Union[str, List[str]]
    ai_config: AIConfig


def get_config_from_path(path: str):
    """Reads given config file and parses it into `BotConfig`"""
    with open(path, "r") as file:
        data = json.loads(file.read())
    return BotConfig(
        data.get("TOKEN"),
        data.get("INTENTS"),
        data.get("DATA_PATH"),
        data.get("PREFIX"),
        AIConfig(
            data.get("AI_CONFIG", {"api_key": ""}).get("api_key"),
            data.get("AI_CONFIG", {"dm_respond": False}).get("dm_respond")
        )
    )


class MuffinBot(commands.Bot):
    """Bot class derived from `commands.Bot` that has additional commands specifically for our purposes"""

    def __init__(self, config_filename: str):
        self.config_path = config_filename

        # Load config
        self.config: BotConfig = get_config_from_path(self.config_path)

        # Create intents
        intents = discord.Intents()
        for intent in self.config.intents:
            setattr(intents, intent.lower(), True)

        # Setup commands.Bot
        super(MuffinBot, self).__init__(self.config.command_prefix, help_command=None,
                                        description="GPT-3 Powered Help Bot", intents=intents, case_insensitive=True)

        # Load extensions
        with open("extensions.txt", "r") as file:
            for line in file:
                if line.startswith("#") or line.strip() == "":
                    continue
                self.load_extension(line.strip())

    async def on_ready(self):
        print(f"Bot is ready!\n"
              f"========================================\n"
              f"User:\t\t\t{self.user}\n"
              f"ID:\t\t\t\t{self.user.id}\n"
              f"Guild Count:\t{len(self.guilds)}\n"
              f"========================================")
        active_intents = [i[0].upper() for i in list(self.intents) if i[1]]
        print(f"Running with intents: {', '.join(active_intents)}")

    def get_data_path(self, path: str = ""):
        """Gets file path relative to bot data path"""
        path = os.path.join(self.data_path, path)
        dir_path = pathlib.Path(os.path.dirname(path))
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return path

    def run(self, *args, **kwargs):
        """Starts the bot with TOKEN in the config"""
        # Get token
        token = self.config.token

        # Destroy token in memory
        self.config.token = None

        super().run(token, *args, **kwargs)


class MuffinCog(commands.Cog):
    """Cog class derived from `commands.Cog` to keep additional attributes"""
    __slots__ = "bot"
    category = "other"

    def __init__(self, bot: MuffinBot):
        self.bot: MuffinBot = bot
