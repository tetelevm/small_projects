import asyncio
import datetime
import random
from pathlib import Path


QUOTES_PATH = Path(__file__).parent / "quotes.txt"


def get_quote(path: Path = QUOTES_PATH):
    with open(path.absolute()) as file:
        data = file.read().splitlines()

    quotes = list(filter(lambda l: l and not l.startswith("#"), data))
    return random.choice(quotes)


async def wait_6_am():
    now = datetime.datetime.now(datetime.UTC)
    am6 = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now > am6:
        am6 += datetime.timedelta(days=1)

    await asyncio.sleep((am6 - now).seconds)
