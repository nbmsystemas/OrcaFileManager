from textual.containers import Horizontal
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from textual.events import MouseDown, MouseMove, MouseUp
from pathlib import Path
from orca.widgets.file_list import FileList
from orca.preview import get_preview


class PreviewPanel(Static):
    DEFAULT_CSS = """
    PreviewPanel {
        height: 100%;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def show_preview(self, path: Path):
        # Use real panel size; fall back to 80x40 if the widget hasn't been laid out yet
        w = self.size.width - 4 if self.size.width > 4 else 80
        h = self.size.height - 2 if self.size.height > 2 else 40
        self.update(get_preview(path, max_w=w, max_h=h))


class ColumnDivider(Static):
    """Draggable divider bar between the two panels."""

    DEFAULT_CSS = """
    ColumnDivider {
        width: 1;
        height: 100%;
    }
    ColumnDivider:hover {
        background: $accent 50%;
    }
    """

    def __init__(self, **kwargs):
        super().__init__("┃", **kwargs)
        self._dragging = False
        self._drag_start_x = 0

    def on_mouse_down(self, event: MouseDown):
        self._dragging = True
        self._drag_start_x = event.screen_x
        self.capture_mouse()
        event.stop()

    def on_mouse_move(self, event: MouseMove):
        if not self._dragging:
            return
        delta_chars = event.screen_x - self._drag_start_x
        if abs(delta_chars) >= 2:
            screen_width = self.app.size.width or 100
            delta_pct = int((delta_chars / screen_width) * 100)
            if delta_pct != 0:
                self.post_message(MillerColumns.DividerDragged(delta_pct))
                self._drag_start_x = event.screen_x
        event.stop()

    def on_mouse_up(self, event: MouseUp):
        self._dragging = False
        self.release_mouse()
        event.stop()


class MillerColumns(Horizontal):

    current_path = reactive(Path.home())
    highlighted_path = reactive(None)

    class DividerDragged(Message):
        def __init__(self, delta_pct: int):
            self.delta_pct = delta_pct
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # [file_list_width, preview_width] as percentages
        self._col_widths = [48, 50]

    def compose(self):
        self.file_list = FileList(id="current-col")
        self.preview_panel = PreviewPanel(id="preview-col")
        self._divider = ColumnDivider()

        yield self.file_list
        yield self._divider
        yield self.preview_panel

    def on_mount(self):
        self.apply_widths()
        self.file_list.load_path(self.current_path)
        self.file_list.focus()

    def apply_widths(self):
        self.file_list.styles.width = f"{self._col_widths[0]}%"
        self.preview_panel.styles.width = f"{self._col_widths[1]}%"

    def adjust_width(self, delta: int):
        """Keyboard shortcut: shrink/expand file list column."""
        new_list = max(15, min(75, self._col_widths[0] + delta))
        self._col_widths = [new_list, 100 - new_list - 2]
        self.apply_widths()

    def on_miller_columns_divider_dragged(self, event: DividerDragged):
        new_list = max(15, min(75, self._col_widths[0] + event.delta_pct))
        self._col_widths = [new_list, 100 - new_list - 2]
        self.apply_widths()

    def watch_current_path(self, new_path: Path):
        self.file_list.load_path(new_path)
        self.file_list.focus()
        self.preview_panel.show_preview(new_path)
        self.highlighted_path = None

    def on_option_list_option_highlighted(self, event):
        if event.option.id:
            path = Path(event.option.id)
            self.highlighted_path = path
            self.preview_panel.show_preview(path)

    def on_file_list_directory_changed(self, event):
        self.current_path = event.path

    def go_up(self):
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
