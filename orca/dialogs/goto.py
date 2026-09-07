from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from pathlib import Path

class GotoDialog(ModalScreen[Path]):
    CSS = '''
    GotoDialog {
        align: center middle;
    }
    #dialog {
        padding: 1 2;
        width: 60;
        height: 10;
        border: solid green;
        background: $surface;
    }
    '''

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("Go to path:")
            yield Input(placeholder="/path/to/dir", id="path_input")

    def on_input_submitted(self, event: Input.Submitted):
        path = Path(event.value).expanduser()
        if path.exists() and path.is_dir():
            self.dismiss(path)
        else:
            self.query_one(Input).styles.border = ("solid", "red")
