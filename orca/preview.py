import os
from pathlib import Path
from rich.syntax import Syntax
from rich.text import Text
from orca.utils import format_size, format_date

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.ico'}

def render_image(path: Path) -> Text:
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB")
        # Terminal characters are roughly 2x taller than wide.
        max_w, max_h = 60, 30
        img.thumbnail((max_w, max_h * 2), Image.Resampling.LANCZOS)
        
        # Ensure height is even for half-block rendering
        if img.height % 2 != 0:
            img = img.crop((0, 0, img.width, img.height - 1))
            
        lines = []
        for y in range(0, img.height, 2):
            line = Text()
            for x in range(img.width):
                r1, g1, b1 = img.getpixel((x, y))
                r2, g2, b2 = img.getpixel((x, y+1))
                line.append("▀", style=f"rgb({r1},{g1},{b1}) on rgb({r2},{g2},{b2})")
            lines.append(line)
            
        return Text("\n").join(lines)
    except Exception as e:
        return Text(f"Error loading image: {str(e)}", style="red")

def get_preview(path: Path) -> object:
    if not path.exists():
        return Text("File does not exist.", style="red")
        
    if path.is_dir():
        try:
            items = list(path.iterdir())
            return Text(f"Directory: {path.name}\nItems: {len(items)}\n", style="blue")
        except PermissionError:
            return Text("Permission Denied.", style="red")
            
    if path.suffix.lower() in IMAGE_EXTS:
        return render_image(path)
        
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
