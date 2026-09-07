import os
import subprocess
from pathlib import Path
from subprocess import call
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header

from orca.utils import open_with_default_application
from orca.widgets.miller_columns import MillerColumns

THEMES = ["default", "transparent", "pink", "carbon"]

# CSS loaded as user CSS (highest priority, overrides Textual defaults).
# OptionList renders its rows with classes, not child widget type selectors.
_THEME_CSS = """
/* ── Transparent theme ─────────────────────────────────────── */
Screen.theme-transparent {
    background: transparent;
}
Screen.theme-transparent Header {
    background: transparent;
}
Screen.theme-transparent Footer {
    background: transparent;
}
Screen.theme-transparent MillerColumns {
    background: transparent;
}
Screen.theme-transparent FileList {
    background: transparent;
}
Screen.theme-transparent OptionList {
    background: transparent;
}
Screen.theme-transparent PreviewPanel {
    background: transparent;
}
Screen.theme-transparent ColumnDivider {
    background: transparent;
    color: #ffffff 40%;
}
Screen.theme-transparent .option-list--option {
    background: transparent;
}
Screen.theme-transparent .option-list--option-highlighted {
    background: #ffffff 15%;
}
Screen.theme-transparent .option-list--option-hover {
    background: #ffffff 8%;
}

/* ── Pink (Synthwave) ────────────────────────────────────────── */
Screen.theme-pink {
    background: #2b112c;
}
Screen.theme-pink Header {
    background: #2b112c;
}
Screen.theme-pink Footer {
    background: #2b112c;
}
Screen.theme-pink MillerColumns {
    background: #2b112c;
}
Screen.theme-pink FileList {
    background: #2b112c;
}
Screen.theme-pink OptionList {
    background: #2b112c;
    color: #ffb6c1;
}
Screen.theme-pink .option-list--option-highlighted {
    background: #ff3366 20%;
}
Screen.theme-pink PreviewPanel {
    background: #3e1236;
    color: #ffb6c1;
}
Screen.theme-pink ColumnDivider {
    background: #ff3399;
}

/* ── Carbon ──────────────────────────────────────────────────── */
Screen.theme-carbon {
    background: #1e1e1e;
}
Screen.theme-carbon Header {
    background: #1e1e1e;
}
Screen.theme-carbon Footer {
    background: #1e1e1e;
}
Screen.theme-carbon MillerColumns {
    background: #1e1e1e;
}
Screen.theme-carbon FileList {
    background: #1e1e1e;
}
Screen.theme-carbon OptionList {
    background: #1e1e1e;
    color: #dddddd;
}
Screen.theme-carbon .option-list--option-highlighted {
    background: #3a3a3a;
}
Screen.theme-carbon PreviewPanel {
    background: #252525;
    color: #dddddd;
}
Screen.theme-carbon ColumnDivider {
    background: #555555;
}
"""


class OrcaApp(App):
    CSS_PATH = "themes/default.tcss"
    CSS = _THEME_CSS

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit"),
        Binding("h", "go_up", "Parent Dir"),
        Binding("backspace", "go_up", "Parent Dir"),
        Binding("l", "enter_dir", "Enter Dir"),
        Binding("tilde", "go_home", "Home"),
        Binding("ctrl+g", "goto_path", "Go to Path"),
        Binding("e", "edit_file", "Edit File"),
        Binding("[", "shrink_cols", "Shrink"),
        Binding("]", "expand_cols", "Expand"),
        Binding("ctrl+h", "toggle_hidden", "Hidden Files"),
        Binding("/", "go_root", "Root /"),
        Binding("t", "cycle_theme", "Theme"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        self.columns = MillerColumns()
        yield self.columns
        yield Footer()

    def on_mount(self):
        self.title = "OrcaFileManager 🐋"
        self.theme_idx = 1  # Start on transparent
        self._set_theme(THEMES[self.theme_idx])

    def _set_theme(self, selected_theme: str):
        for theme in THEMES:
            self.screen.remove_class(f"theme-{theme}")
        if selected_theme != "default":
            self.screen.add_class(f"theme-{selected_theme}")

    def action_go_up(self):
        self.columns.go_up()

    def action_go_home(self):
        self.columns.current_path = Path.home()

    def action_go_root(self):
        self.columns.current_path = Path("/")

    def action_enter_dir(self):
        """Open the highlighted directory or regular file."""
        path = self.columns.highlighted_path
        if not path:
            return
        if path.is_dir():
            self.columns.current_path = path
        elif path.is_file():
            self.on_file_list_file_selected(self.columns.file_list.FileSelected(path))

    def action_goto_path(self):
        from orca.dialogs.goto import GotoDialog

        def check_path(path: Path | None):
            if path is not None:
                self.columns.current_path = path

        self.push_screen(GotoDialog(), check_path)

    def action_edit_file(self):
        path = self.columns.highlighted_path
        if path and path.is_file():
            editor = os.environ.get("EDITOR", "nano")
            with self.suspend():
                call([editor, str(path)])

    def action_shrink_cols(self):
        self.columns.adjust_width(-5)

    def action_expand_cols(self):
        self.columns.adjust_width(5)

    def action_toggle_hidden(self):
        self.columns.file_list.toggle_hidden()
        is_shown = self.columns.file_list.show_hidden
        self.notify(
            f"Hidden files {'visible' if is_shown else 'hidden'}",
            title="Ctrl+H",
            timeout=2,
        )

    def on_file_list_file_selected(self, event):
        try:
            open_with_default_application(event.path)
        except (OSError, subprocess.SubprocessError) as exc:
            self.notify(
                f"Could not open {event.path.name}: {exc}",
                title="Open failed",
                severity="error",
                timeout=4,
            )

    def action_cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        next_theme = THEMES[self.theme_idx]
        self._set_theme(next_theme)
        self.notify(f"Theme: {next_theme}", timeout=1)


if __name__ == "__main__":
    app = OrcaApp()
    app.run()
