# discord-bot

## Overview

A discord bot, configurable to have fitting modules for the use case.

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

```
TOKEN=<bot-token>
```

Then run the following command to set up the database:

> python -m src.db.sqlite_setup

Build the container using this command:

> docker build -t discord-bot .

## Configuration

In the [config file](./config/config.yaml) the theme for the bot can be set and modules can be turned on or off (true is on/false is off). After changing any values the container needs to be rebuilt (see [Setup/installation](#setupinstallation)).

## Usage/examples

Runs the container built in [Setup/installation](#setupinstallation)

```
docker run -d \
  --name dc-bot \
  --restart unless-stopped \
  -v $(pwd)/database.db:/app/database.db \
  discord-bot
```

<!-- ## Validation/testing -->

## Troubleshooting

Check the logs:

> docker logs -f dc-bot

## References/resources

[discord.py](https://discordpy.readthedocs.io/en/stable/)
