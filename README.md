# discord-bot

## Overview

A general-purpose Discord bot built from independent, toggleable modules: casino games, a countdown, music playback, and a todo list. Each deployment only runs what it needs.

## Prerequisites

- Docker

## Architecture

- [./audio_files/](./audio_files/) contains .mp3 files that can be played in a voice channel
- [./config/](./config/) contains the configuration file
- [./src/bot/](./src/bot/) contains generic discord bot setup
- [./src/commands/](./src/commands/) contains generic discord bot commands
- [./src/db/](./src/db/) contains database logic
- [./src/modules/](./src/modules/) contains more specific commands and functionalities, every module can be toggled on or off in ./config

## Setup/installation

First create a .env file structured as follows:

```txt
TOKEN=<bot-token>
```

Database tables are created automatically on the bot's first startup.

Build the container using this command:

> docker build -t discord-bot .

## Configuration

In the [config file](./config/config.yaml) the active theme can be set and modules can be turned on or off (`true` is on, `false` is off). A theme bundles the command prefix, the bot's status message, and module-specific text such as countdown messages (see the `themes` section of the config for the available options). After changing any values the container needs to be rebuilt (see [Setup/installation](#setupinstallation)).

## Usage/examples

Runs the container built in [Setup/installation](#setupinstallation)

```bash
docker run -d \
  --name dc-bot \
  --restart unless-stopped \
  -v $(pwd)/database.db:/app/database.db \
  discord-bot
```

Once running, use the active theme's prefix (`b!` by default) to talk to the bot, e.g. `b!help` to list available commands.

## Troubleshooting

Check the logs:

> docker logs -f dc-bot

## References/resources

[discord.py](https://discordpy.readthedocs.io/en/stable/)
