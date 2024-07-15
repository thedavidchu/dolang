import sys
from subprocess import run


def get_top_level_path() -> str:
    top_level_path = run(
        "git rev-parse --show-toplevel".split(),
        capture_output=True,
        timeout=60,
        text=True,
    ).stdout.strip()
    return top_level_path


def add_compiler_to_sys_path():
    sys.path.append(f"{get_top_level_path()}/src")
