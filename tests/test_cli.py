"""Unit tests for Typer CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from godot_engine_mcp.cli import app

runner = CliRunner()


def test_cli_version_command() -> None:
    """Test `godot-mcp version` CLI command."""
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "Godot MCP Environment" in res.stdout
    assert "godot-mcp Version" in res.stdout


def test_cli_probe_command() -> None:
    """Test `godot-mcp probe` CLI command."""
    res = runner.invoke(app, ["probe"])
    assert res.exit_code == 0
    assert "Godot Connection Capabilities" in res.stdout
    assert "Live Editor Bridge" in res.stdout


def test_cli_install_addon_command(temp_project_dir: Path) -> None:
    """Test `godot-mcp install-addon <path>` CLI command."""
    res = runner.invoke(app, ["install-addon", str(temp_project_dir)])
    assert res.exit_code == 0
    assert "Installed godot_mcp addon to" in res.stdout

    installed_cfg = temp_project_dir / "addons" / "godot_mcp" / "plugin.cfg"
    assert installed_cfg.exists()
    assert 'name="Godot MCP"' in installed_cfg.read_text(encoding="utf-8")
