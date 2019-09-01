import argparse
import logging
import logging.handlers
import os
import sys

import config
from bot import SnipeBot
from data import api

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
            api.switchDatabase(api.Environment.dev)
        elif args.env == 'live':
            api.switchDatabase(api.Environment.live)


def main():
    create_log_dir()
    setup_logging()
    read_env_vars()

    # Read and Verify config
    CLUB_DAY = -1
    START_TIME = -1
    END_TIME = -1
    try:
        CLUB_DAY = config.club_day
        START_TIME = config.club_time_start
        END_TIME = config.club_time_stop
    except:
        log.warning('Could not resolve club day, start, and/or stop in config')

    # region Initialize and Run bot

    bot = SnipeBot(CLUB_DAY, START_TIME, END_TIME)

    bot.run(config.token)

    # endregion Initialize and Run bot


if __name__ == "__main__":
    main()
