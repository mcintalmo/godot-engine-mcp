"""Headless CLI client executing Godot operations via subprocess and domain mixins."""

from godot_engine_mcp.client.headless.base import BaseHeadlessClient
from godot_engine_mcp.client.headless.diagnostics_automation_mixin import (
    DiagnosticsAutomationHeadlessMixin,
)
from godot_engine_mcp.client.headless.physics_mixin import PhysicsHeadlessMixin
from godot_engine_mcp.client.headless.project_mixin import ProjectHeadlessMixin
from godot_engine_mcp.client.headless.rendering_mixin import RenderingHeadlessMixin
from godot_engine_mcp.client.headless.scene_mixin import SceneHeadlessMixin
from godot_engine_mcp.client.headless.script_lsp_mixin import ScriptLSPHeadlessMixin
from godot_engine_mcp.client.headless.world_audio_mixin import WorldAudioHeadlessMixin


class HeadlessCLIClient(
    ProjectHeadlessMixin,
    SceneHeadlessMixin,
    ScriptLSPHeadlessMixin,
    PhysicsHeadlessMixin,
    RenderingHeadlessMixin,
    WorldAudioHeadlessMixin,
    DiagnosticsAutomationHeadlessMixin,
    BaseHeadlessClient,
):
    """Fallback client executing Godot commands and operations headlessly via CLI subprocess."""
