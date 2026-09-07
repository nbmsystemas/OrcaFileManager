from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import stat

class EntryType(Enum):
    FILE = "file"
    DIR = "dir"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"

@dataclass
class FileEntry:
    path: Path
    name: str
    is_dir: bool
    size: int
    modified_time: float
    permissions: str
    is_hidden: bool
    
    @classmethod
    def from_path(cls, p: Path) -> "FileEntry":
        try:
            stat_result = p.stat()
            size = stat_result.st_size
            mtime = stat_result.st_mtime
            mode = stat_result.st_mode
            perms = stat.filemode(mode)
        except OSError:
            size, mtime, perms = 0, 0.0, "---------"
            
        return cls(
            path=p,
            name=p.name,
            is_dir=p.is_dir(),
            size=size,
            modified_time=mtime,
            permissions=perms,
            is_hidden=p.name.startswith('.')
        )
