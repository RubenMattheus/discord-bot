#!/bin/bash

python -B ./src/data/sqlite_setup.py

nohup python -B ./src/bot/bot.py >> log.txt 2>&1 &