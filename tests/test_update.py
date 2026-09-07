import subprocess
import sys

import pytest

from orca.__main__ import build_update_command, do_update

REPOSITORY = "https://github.com/nbmsystemas/OrcaFileManager.git"


def test_regular_update_forces_a_fresh_github_install():
    assert build_update_command(
        pipx=False,
        python_executable="/venv/bin/python",
    ) == [
        "/venv/bin/python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--force-reinstall",
        "--no-cache-dir",
        f"git+{REPOSITORY}",
    ]


def test_pipx_update_forces_install_from_github():
    assert build_update_command(
        pipx=True,
        pipx_executable="/usr/local/bin/pipx",
    ) == [
        "/usr/local/bin/pipx",
        "install",
        "--force",
        "--pip-args=--no-cache-dir",
        f"git+{REPOSITORY}",
    ]


def test_update_reports_missing_pipx(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "executable", "/home/user/.local/pipx/venvs/orca/bin/python"
    )
    monkeypatch.setattr("orca.__main__.shutil.which", lambda name: None)

    with pytest.raises(SystemExit) as exc_info:
        do_update()

    assert exc_info.value.code == 1
    assert "pipx" in capsys.readouterr().out


def test_update_converts_subprocess_failures_to_a_failed_exit(monkeypatch, capsys):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("pip is unavailable")),
    )

    with pytest.raises(SystemExit) as exc_info:
        do_update()

    assert exc_info.value.code == 1
    assert "pip is unavailable" in capsys.readouterr().out
