import argparse
import contextlib
import json
import logging
import logging.handlers

import cogs.utils.db as Database
from bot import SnipeBot


@contextlib.contextmanager
def setup_logging():
    try:
        logging.getLogger('discord').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(level=logging.INFO)
        handler = logging.handlers.RotatingFileHandler(filename='snipebot.log', encoding='utf-8', maxBytes=10485760, backupCount=5)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s', dt_fmt)
        handler.setFormatter(fmt)
        log.addHandler(handler)
        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dev', action='store_true', help='use the dev database')
    args = parser.parse_args()

    Database.switch_database(Database.Environment.LIVE)
    if args.dev:
        Database.switch_database(Database.Environment.DEV)

    # Read and Verify config
    with open('config.json') as config_file:
        config = json.load(config_file)

    with setup_logging():
        # Initialize and Run bot
        bot = SnipeBot(config)

        bot.run()


if __name__ == "__main__":
    main()
