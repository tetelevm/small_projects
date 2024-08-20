import datetime
import random
from pathlib import Path

from settings import SENDING_TIME, QUOTES_PATH


__all__ = [
    "get_quote",
    "calc_waiting_seconds",
]


def get_quote(path: Path = QUOTES_PATH) -> str:
    """
    Reads data files, filters and returns a random quote.
    The reading is performed each time before a choice to allow updating
    the data without restarting the project.
    """

    with open(path.absolute()) as file:
        data = file.read().splitlines()

    quotes = list(filter(lambda l: l and not l.startswith("#"), data))
    return random.choice(quotes).lower()


def calc_waiting_seconds() -> int:
    now = datetime.datetime.now(datetime.UTC)
    today = datetime.datetime.combine(now, datetime.time(), tzinfo=datetime.UTC)
    sending_datetime = today + SENDING_TIME

    if now > sending_datetime:
        sending_datetime += datetime.timedelta(days=1)

    waiting_time = (sending_datetime - now).seconds
    return waiting_time
