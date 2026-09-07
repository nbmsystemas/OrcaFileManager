import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

__all__ = ["format_date", "format_size", "open_with_default_application"]


def open_with_default_application(
    path: Path,
    *,
    platform_name: str | None = None,
    runner=None,
    startfile=None,
) -> None:
    """Open a regular file with the platform's default application.

    ``runner`` and ``startfile`` are injectable so callers can test command
    construction without launching an external application.
    """
    path = Path(path)
    platform_name = platform_name or sys.platform

    if platform_name.startswith("win"):
        opener = startfile or getattr(os, "startfile", None)
        if opener is None:
            raise OSError("Windows default application opener is unavailable")
        opener(str(path))
        return

    command_name = "open" if platform_name == "darwin" else "xdg-open"
    if shutil.which(command_name) is None:
        raise FileNotFoundError(f"{command_name} is not available; cannot open {path}")

    command = [command_name, str(path)]
    (runner or subprocess.run)(command, check=True)


def format_size(size: int) -> str:
    value = size * 1.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def format_date(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
