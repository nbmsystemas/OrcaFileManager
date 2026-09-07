import os
from pathlib import Path
from rich.syntax import Syntax
from rich.text import Text
from orca.utils import format_size, format_date

def get_preview(path: Path) -> object:
    if not path.exists():
        return Text("File does not exist.", style="red")
        
    if path.is_dir():
        try:
            items = list(path.iterdir())
            return Text(f"Directory: {path.name}\nItems: {len(items)}\n", style="blue")
        except PermissionError:
            return Text("Permission Denied.", style="red")
            
    # Try reading as text
    try:
        if path.stat().st_size > 1024 * 1024:  # > 1MB
            return Text(f"File too large to preview ({format_size(path.stat().st_size)}).", style="yellow")
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(2048)  # Read first 2KB
            if len(content) == 2048:
                content += "\n... [truncated]"
                
        return Syntax(
            content,
            lexer=path.suffix.lstrip('.') or 'text',
            line_numbers=True,
            word_wrap=True,
            theme="monokai"
        )
    except UnicodeDecodeError:
        # Binary or image file
        return Text(f"Binary file\nSize: {format_size(path.stat().st_size)}", style="italic")
    except Exception as e:
        return Text(f"Error previewing file: {str(e)}", style="red")
