"""Modular Headless CLI client components and domain mixins."""

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

__all__ = [
    "BaseHeadlessClient",
    "DiagnosticsAutomationHeadlessMixin",
    "PhysicsHeadlessMixin",
    "ProjectHeadlessMixin",
    "RenderingHeadlessMixin",
    "SceneHeadlessMixin",
    "ScriptLSPHeadlessMixin",
    "WorldAudioHeadlessMixin",
]
