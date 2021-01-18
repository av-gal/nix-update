import os
import re
import subprocess
import sys
from pathlib import Path
from typing import IO, Any, Callable, List, Optional, Union, Dict

HAS_TTY = sys.stdout.isatty()
ROOT = Path(os.path.dirname(os.path.realpath(__file__)))


def color_text(code: int, file: IO[Any] = sys.stdout) -> Callable[[str], None]:
    def wrapper(text: str) -> None:
        if HAS_TTY:
            print(f"\x1b[{code}m{text}\x1b[0m", file=file)
        else:
            print(text, file=file)

    return wrapper


warn = color_text(31, file=sys.stderr)
info = color_text(32)


def run(
    command: List[str],
    cwd: Optional[Union[Path, str]] = None,
    stdout: Union[None, int, IO[Any]] = subprocess.PIPE,
    check: bool = True,
    extra_env: Dict[str, str] = {},
) -> "subprocess.CompletedProcess[str]":
    info("$ " + " ".join(command))
    env = os.environ.copy()
    env.update(extra_env)
    return subprocess.run(
        command, cwd=cwd, check=check, text=True, stdout=stdout, env=env
    )


def extract_version(version: str, version_regex: str) -> Optional[str]:
    pattern = re.compile(version_regex)
    match = re.match(pattern, version)
    if match is not None:
        group = match.group(1)
        if group is not None:
            return group
    return None


def version_is_stable(version: str) -> bool:
    filters = ["rc", "alpha", "beta", "preview", "nightly", "m[0-9]"]
    filters_in_version = [x for x in filters if re.search(x, version, re.IGNORECASE)]
    return version is not None and (not any(filters_in_version))
