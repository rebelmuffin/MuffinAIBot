# Muffin AI Bot
An extensively customizable language generating discord bot powered by OpenAI GPT-3

The API operations are just `openai` library functions wrapped in coroutines for now. (Very easy to implement my own solution but I didn't have much time when I first created this. I'll do that soon, or you can send a pull request, then I would be happy to merge some neat code)

This bot is highly experimental, and you need OpenAI beta access to use it. It also needs a lot of refactoring which I will get to when I have the time.

Feel free to fork it and do whatever changes you want, and give me a heads up. I would love to see your fork ;)

The code will go through a huge refactoring very soon, so keep that in mind if you want to fork it.

## Usage
You need a JSON file named `config.json` for configuration of the BOT and API.
Example:
```json
{
  "TOKEN": "MTk4NjIyNDgzNDcxOTI1MjQ4.Cl2FMQ.ZnCjm1XVW7vRze4b7Cq4se7kKWs",
  "INTENTS": [
    "guilds",
    "members",
    "bans",
    "emojis",
    "integrations",
    "webhooks",
    "invites",
    "voice_states",
    "presences",
    "messages",
    "guild_messages",
    "dm_messages",
    "reactions",
    "guild_reactions",
    "dm_reactions",
    "typing",
    "guild_typing",
    "dm_typing"
  ],
  "DATA_PATH": "data",
  "PREFIX": "$",
  "AI_CONFIG": {
    "api_key": "YOUR_OPENAI_KEY",
    "dm_respond": false
  }
}
```

Contexts located in `data` folder has all the information OpenAI API needs to generate text. You can write your own contexts and use them in code.

###CONTEXTS EXPLANATION COMING SOON (more like when I find the time)
