"""Unit tests for config and version parsing."""

from pathlib import Path

from godot_mcp.config import GodotConfig


def test_parse_version_string_standard() -> None:
    """Test parsing standard Godot version strings."""
    parsed = GodotConfig.parse_version_string("4.7.1.stable.official.abc1234")
    assert parsed["major"] == 4
    assert parsed["minor"] == 7
    assert parsed["patch"] == 1
    assert parsed["status"] == "stable"


def test_parse_version_string_beta() -> None:
    """Test parsing beta / dev Godot version strings."""
    parsed = GodotConfig.parse_version_string("4.8.0.beta2")
    assert parsed["major"] == 4
    assert parsed["minor"] == 8
    assert parsed["patch"] == 0
    assert parsed["status"] == "beta2"


def test_discover_project_root(temp_project_dir: Path) -> None:
    """Test discovery of project.godot by walking up directories."""
    sub_dir = temp_project_dir / "scenes" / "nested"
    sub_dir.mkdir(parents=True)

    discovered = GodotConfig.discover_project_root(start_dir=sub_dir)
    assert discovered == str(temp_project_dir.resolve())
