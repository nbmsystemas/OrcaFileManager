from pathlib import Path

from rich.console import RenderableType
from rich.syntax import Syntax
from rich.text import Text

from orca.utils import format_size

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".ico"}


def render_image(path: Path, max_w: int = 80, max_h: int = 40) -> Text:
    try:
        from PIL import Image

        # Half-block characters use one terminal cell for two pixel rows. Clamp
        # the available area so tiny panels never produce a zero-sized image.
        width_limit = max(1, int(max_w))
        height_limit = max(1, int(max_h)) * 2

        source = Image.open(path).convert("RGBA")
        # Rich receives explicit RGB colors, so flatten alpha against a fixed
        # black background instead of relying on a renderer-specific default.
        background = Image.new("RGBA", source.size, (0, 0, 0, 255))
        img = Image.alpha_composite(background, source).convert("RGB")
        img.thumbnail((width_limit, height_limit), Image.Resampling.LANCZOS)

        # Preserve a one-pixel-tall image by duplicating its last row rather
        # than cropping it to zero. This also keeps every half-block complete.
        if img.height % 2:
            padded = Image.new("RGB", (img.width, img.height + 1))
            padded.paste(img, (0, 0))
            padded.paste(
                img.crop((0, img.height - 1, img.width, img.height)), (0, img.height)
            )
            img = padded

        lines = []
        for y in range(0, img.height, 2):
            line = Text()
            for x in range(img.width):
                pixel_top = img.getpixel((x, y))
                pixel_bottom = img.getpixel((x, y + 1))
                if not isinstance(pixel_top, tuple) or not isinstance(
                    pixel_bottom, tuple
                ):
                    continue
                r1, g1, b1 = pixel_top[:3]
                r2, g2, b2 = pixel_bottom[:3]
                line.append("▀", style=f"rgb({r1},{g1},{b1}) on rgb({r2},{g2},{b2})")
            lines.append(line)

        return Text("\n").join(lines)
    except (OSError, ValueError) as e:
        return Text(f"Error loading image: {e!s}", style="red")


def get_preview(path: Path, max_w: int = 80, max_h: int = 40) -> RenderableType:
    if not path.exists():
        return Text("File does not exist.", style="red")

    if path.is_dir():
        try:
            items = list(path.iterdir())
            return Text(f"Directory: {path.name}\nItems: {len(items)}\n", style="blue")
        except PermissionError:
            return Text("Permission Denied.", style="red")

    if path.suffix.lower() in IMAGE_EXTS:
        return render_image(path, max_w=max_w, max_h=max_h)

    # Try reading as text
    try:
        if path.stat().st_size > 1024 * 1024:  # > 1MB
            return Text(
                f"File too large to preview ({format_size(path.stat().st_size)}).",
                style="yellow",
            )

        with open(path, encoding="utf-8") as f:
            content = f.read(2048)  # Read first 2KB
            if len(content) == 2048:
                content += "\n... [truncated]"

        return Syntax(
            content,
            lexer=path.suffix.lstrip(".") or "text",
            line_numbers=True,
            word_wrap=True,
            theme="monokai",
        )
    except UnicodeDecodeError:
        # Binary or image file
        return Text(
            f"Binary file\nSize: {format_size(path.stat().st_size)}", style="italic"
        )
    except (OSError, LookupError) as e:
        return Text(f"Error previewing file: {e!s}", style="red")
