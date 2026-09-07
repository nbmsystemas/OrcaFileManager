from pathlib import Path
from unittest.mock import Mock, patch

import orca.utils as utils


def test_open_file_uses_xdg_open_on_linux(tmp_path: Path):
    path = tmp_path / "document.pdf"
    path.touch()
    runner = Mock()
    with patch("orca.utils.shutil.which", return_value="/usr/bin/xdg-open"):
        utils.open_with_default_application(path, platform_name="linux", runner=runner)

    runner.assert_called_once_with(["xdg-open", str(path)], check=True)


def test_open_file_uses_open_on_macos(tmp_path: Path):
    path = tmp_path / "document.bin"
    path.touch()
    runner = Mock()
    with patch("orca.utils.shutil.which", return_value="/usr/bin/open"):
        utils.open_with_default_application(path, platform_name="darwin", runner=runner)

    runner.assert_called_once_with(["open", str(path)], check=True)


def test_open_file_uses_startfile_on_windows(tmp_path: Path):
    path = tmp_path / "document.pdf"
    path.touch()
    startfile = Mock()

    utils.open_with_default_application(
        path, platform_name="win32", startfile=startfile
    )

    startfile.assert_called_once_with(str(path))


def test_open_file_reports_missing_linux_opener(tmp_path: Path):
    path = tmp_path / "document.pdf"
    path.touch()

    with patch("orca.utils.shutil.which", return_value=None):
        try:
            utils.open_with_default_application(path, platform_name="linux")
        except FileNotFoundError as exc:
            assert "xdg-open" in str(exc)
        else:
            raise AssertionError("expected a missing opener error")
