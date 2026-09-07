from pathlib import Path

from PIL import Image

from orca.preview import render_image


def test_render_image_keeps_a_tiny_image_visible(tmp_path: Path):
    image_path = tmp_path / "tiny.png"
    Image.new("RGBA", (1, 1), (255, 0, 0, 128)).save(image_path)

    rendered = render_image(image_path, max_w=1, max_h=1)

    assert rendered.plain == "▀"
    assert "Error loading image" not in rendered.plain


def test_render_image_composites_alpha_and_clamps_dimensions(tmp_path: Path):
    image_path = tmp_path / "wide.png"
    Image.new("RGBA", (20, 10), (255, 0, 0, 128)).save(image_path)

    rendered = render_image(image_path, max_w=4, max_h=2)

    assert 1 <= len(rendered.plain.splitlines()) <= 2
    assert all(len(line) <= 4 for line in rendered.plain.splitlines())
    assert rendered.spans
    assert "rgb(128,0,0)" in str(rendered.spans[0].style)


def test_render_image_handles_non_positive_limits(tmp_path: Path):
    image_path = tmp_path / "pixel.png"
    Image.new("RGB", (2, 2), (1, 2, 3)).save(image_path)

    rendered = render_image(image_path, max_w=0, max_h=-1)

    assert rendered.plain == "▀"
