import datetime
from pathlib import Path


__all__ = [
    "QUOTES_PATH",
    "SENDING_TIME",
    "TOKEN",
    "CHAT_LINK",
]

_ENVS: dict[str, str] | None = None


def _read_env():
    env_path = Path(__file__).parent / ".env"
    with open(env_path.absolute()) as file:
        data = file.read().splitlines()

    global _ENVS
    _ENVS = dict(line.split("=") for line in data)


def _env(arg: str):
    if _ENVS is None:
        _read_env()
    return _ENVS[arg]


_ENVS_VERSION = "_TEST"

QUOTES_PATH = Path(__file__).parent / "quotes.txt"
SENDING_TIME = datetime.timedelta(hours=19, minutes=22, seconds=0)

TOKEN = _env("TOKEN" + _ENVS_VERSION)
CHAT_LINK = _env("CHAT_LINK" + _ENVS_VERSION)
