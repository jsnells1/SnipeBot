import argparse
import json
import logging
import logging.handlers
import os
import sys

import cogs.utils.db as Database
from bot import SnipeBot

log = logging.getLogger()


def create_log_dir():
    try:
        os.makedirs('./log', exist_ok=True)
    except:
        sys.exit('Log directory does not exist and cannot be created')


def setup_logging():
    logging.getLogger('discord').setLevel(logging.WARNING)
    log.setLevel(level=logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='./log/snipebot.log', encoding='utf-8', maxBytes=10485760, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    log.addHandler(handler)


def read_env_vars():
    parser = argparse.ArgumentParser()
    parser.add_argument('-env')
    args = parser.parse_args()

    if args.env is not None:
        if args.env == 'dev':
            Database.switch_database(Database.Environment.DEV)
        elif args.env == 'live':
            Database.switch_database(Database.Environment.LIVE)


def main():
    create_log_dir()
    setup_logging()
    read_env_vars()

    # Read and Verify config
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Initialize and Run bot
    bot = SnipeBot(config)

    bot.run()


if __name__ == "__main__":
    main()
