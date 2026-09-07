import os
from subprocess import call
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual.color import Color
from pathlib import Path

from orca.widgets.miller_columns import MillerColumns

THEMES = ["default", "transparent", "pink", "carbon"]

_TRANSPARENT = Color(0, 0, 0, 0)

_THEME_STYLES = {
    "default": {
        "screen": {},
        "header": {},
        "footer": {},
        "file_list": {},
        "preview": {},
        "divider": {},
    },
    "transparent": {
        "screen":   {"background": _TRANSPARENT},
        "header":   {"background": _TRANSPARENT},
        "footer":   {"background": _TRANSPARENT},
        "file_list": {"background": _TRANSPARENT},
        "preview":  {"background": _TRANSPARENT},
        "divider":  {"background": _TRANSPARENT},
    },
    "pink": {
        "screen":   {"background": Color.parse("#2b112c")},
        "header":   {"background": Color.parse("#2b112c")},
        "footer":   {"background": Color.parse("#2b112c")},
        "file_list": {"background": Color.parse("#2b112c")},
        "preview":  {"background": Color.parse("#3e1236")},
        "divider":  {"background": Color.parse("#ff3399")},
    },
    "carbon": {
        "screen":   {"background": Color.parse("#1e1e1e")},
        "header":   {"background": Color.parse("#1e1e1e")},
        "footer":   {"background": Color.parse("#1e1e1e")},
        "file_list": {"background": Color.parse("#1e1e1e")},
        "preview":  {"background": Color.parse("#252525")},
        "divider":  {"background": Color.parse("#555555")},
    },
}


class OrcaApp(App):
    CSS_PATH = "themes/default.tcss"

    BINDINGS = [
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
        self._apply_theme("transparent")

    def _apply_theme(self, name: str):
        styles = _THEME_STYLES.get(name, _THEME_STYLES["default"])

        def _set(widget, key, val):
            setattr(widget.styles, key, val)

        # Screen
        for k, v in styles["screen"].items():
            _set(self.screen, k, v)

        # Header & Footer
        header = self.query_one(Header)
        footer = self.query_one(Footer)
        for k, v in styles["header"].items():
            _set(header, k, v)
        for k, v in styles["footer"].items():
            _set(footer, k, v)

        # Panels inside MillerColumns
        file_list = self.columns.file_list
        preview = self.columns.preview_panel
        divider = self.columns._divider

        for k, v in styles["file_list"].items():
            _set(file_list, k, v)
        for k, v in styles["preview"].items():
            _set(preview, k, v)
        for k, v in styles["divider"].items():
            _set(divider, k, v)

    def action_go_up(self):
        self.columns.go_up()

    def action_go_home(self):
        self.columns.current_path = Path.home()

    def action_go_root(self):
        self.columns.current_path = Path("/")

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

    def action_cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        next_theme = THEMES[self.theme_idx]
        self._apply_theme(next_theme)
        self.notify(f"Theme: {next_theme}", timeout=1)


if __name__ == "__main__":
    app = OrcaApp()
    app.run()
