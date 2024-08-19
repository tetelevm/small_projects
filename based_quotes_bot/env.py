from pathlib import Path


__all__ = ["env"]
_ENVS: dict[str, str] | None = None


def _read_env():
    env_path = Path(__file__).parent / ".env"
    with open(env_path.absolute()) as file:
        data = file.read().splitlines()

    global _ENVS
    _ENVS = dict(line.split("=") for line in data)


def env(arg: str):
    if _ENVS is None:
        _read_env()
    return _ENVS[arg]
