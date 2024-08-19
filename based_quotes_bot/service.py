import asyncio
import datetime
import random
from pathlib import Path

from settings import logger, SENDING_TIME, QUOTES_PATH


def get_quote(path: Path = QUOTES_PATH):
    with open(path.absolute()) as file:
        data = file.read().splitlines()

    quotes = list(filter(lambda l: l and not l.startswith("#"), data))
    return random.choice(quotes)


async def wait_sending_time():
    now = datetime.datetime.now(datetime.UTC)
    today = datetime.datetime.combine(now, datetime.time(), tzinfo=datetime.UTC)
    sending_datetime = today + SENDING_TIME

    if now > sending_datetime:
        sending_datetime += datetime.timedelta(days=1)

    waiting_time = (sending_datetime - now).seconds
    logger.info(f"Waiting {waiting_time} seconds")
    await asyncio.sleep(waiting_time)
