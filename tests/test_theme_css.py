from pathlib import Path

APP_SOURCE = Path(__file__).parents[1] / "orca" / "app.py"


def test_transparent_theme_targets_textual_option_classes():
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "Screen.theme-transparent .option-list--option" in source
    assert "Screen.theme-transparent .option-list--option-highlighted" in source
    assert "Screen.theme-transparent .option-list--option-hover" in source
    assert "OptionList > .option-list--option" not in source


def test_theme_cycle_removes_all_previous_theme_classes():
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "for theme in THEMES:" in source
    assert 'self.screen.remove_class(f"theme-{theme}")' in source
