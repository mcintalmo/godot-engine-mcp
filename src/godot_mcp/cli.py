"""Command-line interface for Godot MCP server."""

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from godot_mcp import __version__
from godot_mcp.client.manager import ClientManager
from godot_mcp.config import GodotConfig
from godot_mcp.server import create_server

app = typer.Typer(
    name="godot-mcp",
    help="Model Context Protocol (MCP) server for Godot Engine 4.7+.",
    no_args_is_help=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    transport: Annotated[
        str, typer.Option("--transport", "-t", help="Transport mode: stdio or sse")
    ] = "stdio",
    host: Annotated[
        str, typer.Option("--host", "-h", help="Host for HTTP transport")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option("--port", "-p", help="Port for HTTP transport")
    ] = 8000,
    godot_path: Annotated[
        str | None, typer.Option("--godot-path", help="Path to Godot binary")
    ] = None,
    project_path: Annotated[
        str | None, typer.Option("--project-path", help="Path to Godot project root")
    ] = None,
) -> None:
    """Default entrypoint - launches the MCP server."""
    if ctx.invoked_subcommand is None:
        cfg = GodotConfig.load()
        if godot_path:
            cfg.executable_path = godot_path
        if project_path:
            cfg.project_path = project_path

        server = create_server(config=cfg)

        if transport == "stdio":
            server.run(transport="stdio")
        else:
            server.run(transport="sse", host=host, port=port)


@app.command()
def version() -> None:
    """Show godot-mcp version and discovered Godot Engine information."""
    cfg = GodotConfig.load()
    vinfo = cfg.get_version_info()

    table = Table(title="Godot MCP Environment")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("godot-mcp Version", __version__)
    table.add_row("Engine Version", vinfo.get("version_string", "Unknown"))
    table.add_row("Godot Executable", cfg.executable_path or "Not found")
    table.add_row("Godot Project Root", cfg.project_path or "Not detected")
    table.add_row("Bridge Host:Port", f"{cfg.bridge_host}:{cfg.bridge_port}")

    console.print(table)


@app.command()
def probe() -> None:
    """Probe Godot connection status (Live Editor Bridge & Headless CLI)."""
    cfg = GodotConfig.load()
    manager = ClientManager(cfg)

    async def _do_probe() -> None:
        live_ok = await manager.live_client.is_available()
        headless_ok = await manager.headless_client.is_available()

        table = Table(title="Godot Connection Capabilities")
        table.add_column("Bridge Layer", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")

        table.add_row(
            "Live Editor Bridge",
            "[green]ONLINE[/green]" if live_ok else "[yellow]OFFLINE[/yellow]",
            f"ws://{cfg.bridge_host}:{cfg.bridge_port}/ws"
            + (" (Active)" if live_ok else " (Start Godot with addon)"),
        )
        table.add_row(
            "Headless CLI",
            "[green]AVAILABLE[/green]" if headless_ok else "[red]UNAVAILABLE[/red]",
            cfg.executable_path or "Godot binary not found in PATH",
        )

        console.print(table)

    asyncio.run(_do_probe())


@app.command()
def install_addon(
    target_project: Annotated[
        Path,
        typer.Argument(
            help="Path to the Godot project root (where project.godot is located)",
        ),
    ],
) -> None:
    """Install or update the godot_mcp EditorPlugin addon into a Godot project."""

    target = target_project.resolve()
    if not (target / "project.godot").is_file():
        console.print(f"[red]Error:[/red] No project.godot found at {target}")
        raise typer.Exit(code=1)

    candidate_sources = [
        Path(__file__).resolve().parent / "addons" / "godot_mcp",
        Path(__file__).resolve().parent.parent / "addons" / "godot_mcp",
        Path(__file__).resolve().parent.parent.parent / "addons" / "godot_mcp",
    ]
    addon_source = next((p for p in candidate_sources if p.is_dir()), None)
    if not addon_source:
        console.print(
            f"[red]Error:[/red] Source addon directory not found in candidates: {candidate_sources}"
        )
        raise typer.Exit(code=1)

    dest = target / "addons" / "godot_mcp"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(addon_source, dest)
    console.print(f"[green]Success:[/green] Installed godot_mcp addon to {dest}")

    # Auto-enable plugin in project.godot
    project_godot_path = target / "project.godot"
    try:
        content = project_godot_path.read_text(encoding="utf-8")
        plugin_path = "res://addons/godot_mcp/plugin.cfg"
        if "[editor_plugins]" not in content:
            content += (
                f'\n[editor_plugins]\n\nenabled=PackedStringArray("{plugin_path}")\n'
            )
            project_godot_path.write_text(content, encoding="utf-8")
            console.print(
                "[green]Enabled:[/green] Registered plugin in project.godot [editor_plugins]"
            )
        elif plugin_path not in content:
            # Append plugin into existing enabled list
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if line.startswith("enabled=PackedStringArray("):
                    inside = line.split("PackedStringArray(")[1].rstrip(")")
                    items = [
                        it.strip().strip('"') for it in inside.split(",") if it.strip()
                    ]
                    if plugin_path not in items:
                        items.append(plugin_path)
                    formatted_items = ", ".join(f'"{it}"' for it in items)
                    new_lines.append(f"enabled=PackedStringArray({formatted_items})")
                else:
                    new_lines.append(line)
            project_godot_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            console.print(
                "[green]Enabled:[/green] Added plugin to existing [editor_plugins]"
            )
        else:
            console.print(
                "[green]Enabled:[/green] Plugin is already configured in project.godot"
            )
    except (OSError, ValueError) as e:
        console.print(
            f"[yellow]Warning:[/yellow] Could not auto-modify project.godot: {e}"
        )


@app.command()
def open_editor(
    project_path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the Godot project root (defaults to auto-discovered project)",
        ),
    ] = None,
) -> None:
    """Launch the Godot Editor for a project directly from the CLI."""
    cfg = GodotConfig.load(project_path=str(project_path) if project_path else None)
    if not cfg.executable_path:
        console.print("[red]Error:[/red] Godot executable not found.")
        raise typer.Exit(code=1)
    if not cfg.project_path:
        console.print("[red]Error:[/red] Godot project path not specified or found.")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Opening Godot Editor for:[/cyan] {cfg.project_path}")
    subprocess.Popen(
        [cfg.executable_path, "-e", "--path", cfg.project_path],
        start_new_session=True,
    )
    console.print("[green]Success:[/green] Godot Editor launched.")


@app.command()
def reload(
    project_path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the Godot project root (defaults to auto-discovered project)",
        ),
    ] = None,
) -> None:
    """Reload the running Godot Editor via live bridge RPC, or launch if offline."""
    cfg = GodotConfig.load(project_path=str(project_path) if project_path else None)
    manager = ClientManager(cfg)

    async def _do_reload() -> None:
        if await manager.live_client.is_available():
            console.print("[cyan]Sending reload signal to live Godot Editor...[/cyan]")
            res = await manager.live_client._send_rpc("restart_editor", {"save": True})
            if res.success:
                console.print("[green]Success:[/green] Godot Editor reload initiated.")
                return

        if cfg.executable_path and cfg.project_path:
            console.print(
                f"[cyan]Launching Godot Editor for:[/cyan] {cfg.project_path}"
            )
            await asyncio.create_subprocess_exec(
                cfg.executable_path, "-e", "--path", cfg.project_path
            )
            console.print("[green]Success:[/green] Godot Editor launched.")
        else:
            console.print("[red]Error:[/red] Could not reload or launch Godot Editor.")

    asyncio.run(_do_reload())
