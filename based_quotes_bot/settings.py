import datetime
import logging
from pathlib import Path


__all__ = [
    "logger",
    "QUOTES_PATH",
    "SENDING_TIME",
    "TOKEN",
    "CHAT_LINK",
]


logger = logging.getLogger("application")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter("{asctime:<23} >>| {msg}", style='{')
_file_handler = logging.FileHandler("logs.log", mode='a')
_file_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)
_terminal_handler = logging.StreamHandler()
_terminal_handler.setFormatter(_formatter)
logger.addHandler(_terminal_handler)


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


_ENVS_VERSION = ""

QUOTES_PATH = Path(__file__).parent / "quotes.txt"
SENDING_TIME = datetime.timedelta(hours=5, minutes=0, seconds=0)  # UTC

TOKEN = _env("TOKEN" + _ENVS_VERSION)
CHAT_LINK = _env("CHAT_LINK" + _ENVS_VERSION)
