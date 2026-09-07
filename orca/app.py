import os
from subprocess import call
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from pathlib import Path

from orca.widgets.miller_columns import MillerColumns

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

    def action_go_up(self):
        self.columns.go_up()
        
    def action_go_home(self):
        self.columns.current_path = Path.home()
        
    def action_goto_path(self):
        from orca.dialogs.goto import GotoDialog
        def check_path(path: Path | None):
            if path is not None:
                self.columns.current_path = path
        self.push_screen(GotoDialog(), check_path)
        
    def action_edit_file(self):
        path = self.columns.highlighted_path
        if path and path.is_file():
            # Suspende la interfaz y lanza el editor del sistema
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

    def action_go_root(self):
        self.columns.current_path = Path("/")

    def action_cycle_theme(self):
        themes = ["", "theme-transparent", "theme-pink", "theme-light-black"]
        current_idx = getattr(self, "theme_idx", 0)
        
        if themes[current_idx]:
            self.screen.remove_class(themes[current_idx])
            
        self.theme_idx = (current_idx + 1) % len(themes)
        
        if themes[self.theme_idx]:
            self.screen.add_class(themes[self.theme_idx])
        
    def on_mount(self):
        self.title = "OrcaFileManager 🐋"

if __name__ == "__main__":
    app = OrcaApp()
    app.run()
