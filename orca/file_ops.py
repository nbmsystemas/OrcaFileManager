import shutil
from pathlib import Path
from send2trash import send2trash
import os

def copy_entry(src: Path, dst_dir: Path) -> Path:
    dst = dst_dir / src.name
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return dst

def move_entry(src: Path, dst_dir: Path) -> Path:
    dst = dst_dir / src.name
    shutil.move(str(src), str(dst))
    return dst

def delete_entry(path: Path, permanent: bool = False):
    if permanent:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    else:
        send2trash(path)

def create_directory(parent: Path, name: str) -> Path:
    new_dir = parent / name
    new_dir.mkdir(parents=True, exist_ok=True)
    return new_dir

def create_file(parent: Path, name: str) -> Path:
    new_file = parent / name
    new_file.touch(exist_ok=True)
    return new_file
