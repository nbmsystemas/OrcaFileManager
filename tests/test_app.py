from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("textual")

from orca.app import OrcaApp


def test_file_selection_opens_regular_files_without_launching_in_test(tmp_path: Path):
    path = tmp_path / "report.pdf"
    path.touch()
    app = OrcaApp()

    with patch("orca.app.open_with_default_application") as opener:
        app.on_file_list_file_selected(SimpleNamespace(path=path))

    opener.assert_called_once_with(path)


def test_file_selection_surfaces_opener_failures(tmp_path: Path):
    path = tmp_path / "report.bin"
    path.touch()
    app = OrcaApp()
    app.notify = Mock()

    with patch(
        "orca.app.open_with_default_application",
        side_effect=OSError("opener unavailable"),
    ):
        app.on_file_list_file_selected(SimpleNamespace(path=path))

    app.notify.assert_called_once()
    assert "opener unavailable" in app.notify.call_args.args[0]
