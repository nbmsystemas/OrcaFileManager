from textual.widgets import OptionList
from textual.widgets.option_list import Option
from pathlib import Path
from orca.models import FileEntry
from textual.message import Message
from textual.reactive import reactive


class FileList(OptionList):

    path = reactive(Path.home())
    show_hidden = reactive(False)

    class FileSelected(Message):
        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    class DirectoryChanged(Message):
        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = []

    def load_path(self, path: Path):
        self.path = path
        self._reload()

    def _reload(self):
        self.clear_options()
        self.entries = []

        path = self.path

        # Add ".." entry to go up (except at filesystem root)
        if path.parent != path:
            self.add_option(Option("📁 ..", id=str(path.parent) + "/__UP__"))

        try:
            items = list(path.iterdir())
        except PermissionError:
            self.add_option(Option("🔒 Permission Denied", disabled=True))
            return
        except OSError as e:
            self.add_option(Option(f"⚠ Error: {e}", disabled=True))
            return

        # Sort: dirs first, then files, both alphabetically case-insensitive
        items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

        for p in items:
            entry = FileEntry.from_path(p)

            # Skip hidden unless show_hidden is True
            if entry.is_hidden and not self.show_hidden:
                continue

            self.entries.append(entry)
            if entry.is_dir:
                icon = "📁"
            elif p.is_symlink():
                icon = "🔗"
            else:
                icon = "📄"

            self.add_option(Option(f"{icon} {entry.name}", id=str(p)))

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self._reload()

    def watch_show_hidden(self, _val: bool):
        # Avoid double reload on initial mount
        if self.entries is not None:
            self._reload()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if not event.option.id:
            return

        option_id = event.option.id

        # Handle ".." navigation
        if option_id.endswith("/__UP__"):
            parent = Path(option_id.replace("/__UP__", ""))
            self.post_message(self.DirectoryChanged(parent))
            return

        selected_path = Path(option_id)
        if selected_path.is_dir():
            self.post_message(self.DirectoryChanged(selected_path))
        else:
            self.post_message(self.FileSelected(selected_path))
