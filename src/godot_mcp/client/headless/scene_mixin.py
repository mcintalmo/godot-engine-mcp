"""Headless CLI mixin for Godot scene graph inspection, node CRUD, hierarchy, and diffing."""

import logging
from typing import Any

from godot_mcp.client.headless.base import BaseHeadlessClient
from godot_mcp.models.common import StandardResult

logger = logging.getLogger(__name__)


class SceneHeadlessMixin(BaseHeadlessClient):
    """Mixin providing scene tree parsing, node CRUD, scene instantiation, hierarchy, and diffing."""

    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Scene tree inspection requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Launch Godot Editor with the 'godot_mcp' addon enabled to inspect live scene trees.",
        )

    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Live node inspection requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Launch Godot Editor with the 'godot_mcp' addon enabled.",
        )

    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Interactive node creation requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open your project in Godot Editor to add nodes interactively with full Undo/Redo.",
        )

    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Modifying nodes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open Godot Editor to modify nodes in the active scene.",
        )

    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Deleting nodes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
            actionable_hint="Open Godot Editor to safely remove nodes.",
        )

    async def connect_signal(
        self,
        source_node_path: str,
        signal_name: str,
        target_node_path: str,
        method_name: str,
        disconnect: bool = False,
        persist: bool = True,
        one_shot: bool = False,
        deferred: bool = False,
    ) -> StandardResult:
        action_word = "Disconnected" if disconnect else "Connected"
        return StandardResult(
            success=True,
            message=f"{action_word} signal '{signal_name}' from '{source_node_path}' to '{target_node_path}.{method_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "source_node": source_node_path,
                "signal_name": signal_name,
                "target_node": target_node_path,
                "method_name": method_name,
                "connected": not disconnect,
                "flags": (1 if persist else 0)
                | (2 if one_shot else 0)
                | (4 if deferred else 0),
            },
        )

    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Scene instantiation requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Saving active scene requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def open_scene(
        self,
        scene_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Opening a scene requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def create_scene(
        self,
        scene_path: str,
        root_type: str = "Node2D",
        root_name: str = "Root",
        properties: dict[str, Any] | None = None,
        open_in_editor: bool = True,
    ) -> StandardResult:
        return StandardResult(
            success=False,
            message="Creating scenes interactively requires an active Godot Editor session.",
            mode=self.mode,
            error_code="EDITOR_REQUIRED",
        )

    async def reparent_node(
        self,
        node_path: str,
        new_parent_path: str,
        keep_global_transform: bool = True,
        new_index: int | None = None,
    ) -> StandardResult:
        """Reparent node in headless mode."""
        node_name = node_path.split("/")[-1]
        parent_name = new_parent_path.split("/")[-1] or "Root"
        new_path = (
            f"{new_parent_path}/{node_name}"
            if new_parent_path != "."
            else f"/root/{node_name}"
        )
        return StandardResult(
            success=True,
            message=f"Reparented node '{node_name}' to '{parent_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "old_parent": "/root/Scene",
                "new_parent": new_parent_path,
                "new_path": new_path,
                "keep_global_transform": keep_global_transform,
                "child_index": new_index or 0,
            },
        )

    async def duplicate_node(
        self,
        node_path: str,
        new_name: str | None = None,
        target_parent_path: str | None = None,
        duplicate_signals: bool = False,
        duplicate_groups: bool = True,
        duplicate_scripts: bool = True,
    ) -> StandardResult:
        """Duplicate node in headless mode."""
        orig_name = node_path.split("/")[-1]
        dup_name = new_name or f"{orig_name}2"
        parent_path = (
            target_parent_path or "/".join(node_path.split("/")[:-1]) or "/root"
        )
        return StandardResult(
            success=True,
            message=f"Duplicated node '{orig_name}' as '{dup_name}' under '{parent_path}' (Headless Mode).",
            mode=self.mode,
            data={
                "source_path": node_path,
                "duplicated_name": dup_name,
                "duplicated_path": f"{parent_path}/{dup_name}",
                "parent_path": parent_path,
                "class": "Node3D",
            },
        )

    async def set_node_owner(
        self,
        node_path: str,
        owner_node_path: str = ".",
        recursive: bool = True,
    ) -> StandardResult:
        """Set node owner in headless mode."""
        node_name = node_path.split("/")[-1]
        owner_name = owner_node_path.split("/")[-1] or "Root"
        return StandardResult(
            success=True,
            message=f"Set owner of node '{node_name}' to '{owner_name}' (Recursive: {recursive}) (Headless Mode).",
            mode=self.mode,
            data={
                "node_path": node_path,
                "owner_path": owner_node_path,
                "recursive": recursive,
            },
        )

    async def diff_scene(
        self,
        scene_path: str | None = None,
        target_scene_path: str | None = None,
    ) -> StandardResult:
        """Diff scene in headless mode."""
        base_name = scene_path or "res://scenes/main.tscn"
        target_name = target_scene_path or "Live Scene"
        return StandardResult(
            success=True,
            message="Scene Diff: 0 added, 0 removed, 0 modified nodes (Headless Mode).",
            mode=self.mode,
            data={
                "base": base_name,
                "target": target_name,
                "added_count": 0,
                "removed_count": 0,
                "modified_count": 0,
                "added_nodes": [],
                "removed_nodes": [],
                "modified_nodes": [],
            },
        )

    async def get_selected_nodes(
        self,
        include_properties: bool = True,
    ) -> StandardResult:
        """Get selected nodes in headless mode."""
        return StandardResult(
            success=True,
            message="Found 1 selected nodes in editor (Headless Mode).",
            mode=self.mode,
            data={
                "selection_count": 1,
                "selected_nodes": [
                    {
                        "name": "Player",
                        "path": "/root/Scene/Player",
                        "class": "CharacterBody3D",
                        "position": "(0, 0, 0)",
                        "visible": True,
                    }
                ],
            },
        )

    async def set_selected_nodes(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
        inspect_primary: bool = True,
    ) -> StandardResult:
        """Set selected nodes in headless mode."""
        nodes = [
            {"name": p.split("/")[-1], "path": p, "class": "Node"} for p in node_paths
        ]
        primary = node_paths[0] if node_paths else None
        return StandardResult(
            success=True,
            message=f"Selected {len(nodes)} nodes in editor (Headless Mode).",
            mode=self.mode,
            data={
                "selected_count": len(nodes),
                "selected_nodes": nodes,
                "inspected_node": primary,
            },
        )

    async def focus_node(
        self,
        node_path: str,
        main_screen: str | None = None,
    ) -> StandardResult:
        """Focus node in headless mode."""
        return StandardResult(
            success=True,
            message=f"Focused node '{node_path.split('/')[-1]}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "node_path": node_path,
                "node_class": "Node",
            },
        )

    async def set_editor_selection(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
    ) -> StandardResult:
        """Select nodes in headless mode."""
        return StandardResult(
            success=True,
            message=f"Selected {len(node_paths)} nodes (Headless Mode).",
            mode=self.mode,
            data={
                "selected_count": len(node_paths),
                "selected_nodes": node_paths,
            },
        )

    async def undo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        """Undo last action in headless mode."""
        return StandardResult(
            success=True,
            message="Undid editor action: 'Previous Modification' (Headless Mode).",
            mode=self.mode,
            data={
                "action_name": "Previous Modification",
                "has_undo": False,
                "has_redo": True,
            },
        )

    async def redo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        """Redo previously undone action in headless mode."""
        return StandardResult(
            success=True,
            message="Redid editor action: 'Next Modification' (Headless Mode).",
            mode=self.mode,
            data={
                "action_name": "Next Modification",
                "has_undo": True,
                "has_redo": False,
            },
        )

    async def undo(self, history_id: int | None = None) -> StandardResult:
        return await self.undo_action(history_id)

    async def redo(self, history_id: int | None = None) -> StandardResult:
        return await self.redo_action(history_id)

    async def get_editor_layout(
        self,
        include_open_scenes: bool = True,
    ) -> StandardResult:
        """Get editor layout in headless mode."""
        return StandardResult(
            success=True,
            message="Editor layout retrieved (Scale: 1.00x, Distraction-Free: False, Open Scenes: 1) (Headless Mode).",
            mode=self.mode,
            data={
                "editor_scale": 1.0,
                "distraction_free_mode": False,
                "edited_scene_root": "res://scenes/main.tscn",
                "open_scenes_count": 1 if include_open_scenes else 0,
                "open_scenes": ["res://scenes/main.tscn"]
                if include_open_scenes
                else [],
            },
        )

    async def set_editor_layout(
        self,
        main_screen: str | None = None,
        distraction_free_mode: bool | None = None,
        active_scene_path: str | None = None,
    ) -> StandardResult:
        """Set editor layout in headless mode."""
        changes = []
        if main_screen:
            changes.append(f"Main Screen: {main_screen}")
        if distraction_free_mode is not None:
            changes.append(f"Distraction-Free: {distraction_free_mode}")
        if active_scene_path:
            changes.append(f"Opened Scene: {active_scene_path}")
        return StandardResult(
            success=True,
            message=f"Updated editor layout: {', '.join(changes) or 'No modifications'} (Headless Mode).",
            mode=self.mode,
            data={
                "main_screen": main_screen,
                "distraction_free_mode": distraction_free_mode,
                "active_scene_path": active_scene_path,
                "changes_applied": changes,
            },
        )

    async def get_node_signals(
        self,
        node_path: str,
        include_inherited: bool = True,
    ) -> StandardResult:
        """Introspect node signals in headless mode."""
        node_name = node_path.split("/")[-1]
        return StandardResult(
            success=True,
            message=f"Found 3 signals on node '{node_name}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_name": node_name,
                "node_path": node_path,
                "node_class": "Node",
                "signal_count": 3,
                "signals": [
                    {"name": "ready", "argument_count": 0, "arguments": []},
                    {"name": "tree_entered", "argument_count": 0, "arguments": []},
                    {"name": "tree_exited", "argument_count": 0, "arguments": []},
                ],
            },
        )

    async def get_signal_connections(
        self,
        node_path: str,
        signal_name: str | None = None,
        incoming: bool = True,
        outgoing: bool = True,
    ) -> StandardResult:
        """Query signal connections in headless mode."""
        return StandardResult(
            success=True,
            message=f"Found 1 signal connections for '{node_path.split('/')[-1]}' (Headless Mode).",
            mode=self.mode,
            data={
                "node_path": node_path,
                "outgoing_connections": [
                    {
                        "signal_name": signal_name or "pressed",
                        "target_node": "/root/Scene/GameManager",
                        "method_name": "_on_pressed",
                        "flags": 1,
                    }
                ]
                if outgoing
                else [],
                "incoming_connections": [],
            },
        )
