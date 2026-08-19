"""Scene and node tools implementation for Godot MCP."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.scene import (
    ConnectSignalInput,
    CreateNodeInput,
    CreateSceneInput,
    DeleteNodeInput,
    GetNodeInput,
    InstantiateSceneInput,
    ListNodesInput,
    ModifyNodeInput,
    OpenSceneInput,
    SaveSceneInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_list_nodes(client: GodotClient, params: ListNodesInput) -> str:
    """List nodes in the active Godot scene tree."""
    result = await client.list_nodes(
        root_path=params.root_path,
        max_depth=params.max_depth,
        include_properties=params.include_properties,
    )
    return format_result(result, params.response_format)


async def handle_get_node(client: GodotClient, params: GetNodeInput) -> str:
    """Inspect a node in the scene tree."""
    result = await client.get_node(
        node_path=params.node_path,
        include_inherited_properties=params.include_inherited_properties,
    )
    return format_result(result, params.response_format)


async def handle_create_node(client: GodotClient, params: CreateNodeInput) -> str:
    """Create a new node in the active scene."""
    result = await client.create_node(
        type_name=params.type_name,
        name=params.name,
        parent_path=params.parent_path,
        properties=params.properties,
        script_path=params.script_path,
    )
    return format_result(result, params.response_format)


async def handle_modify_node(client: GodotClient, params: ModifyNodeInput) -> str:
    """Modify properties of an existing node."""
    result = await client.modify_node(
        node_path=params.node_path,
        properties=params.properties,
    )
    return format_result(result, params.response_format)


async def handle_delete_node(client: GodotClient, params: DeleteNodeInput) -> str:
    """Delete a node from the scene."""
    result = await client.delete_node(node_path=params.node_path)
    return format_result(result, params.response_format)


async def handle_connect_signal(client: GodotClient, params: ConnectSignalInput) -> str:
    """Connect a node signal to a target method."""
    result = await client.connect_signal(
        source_node_path=params.source_node_path,
        signal_name=params.signal_name,
        target_node_path=params.target_node_path,
        method_name=params.method_name,
        flags=params.flags,
    )
    return format_result(result, params.response_format)


async def handle_instantiate_scene(
    client: GodotClient, params: InstantiateSceneInput
) -> str:
    """Instantiate a packed scene file."""
    result = await client.instantiate_scene(
        scene_path=params.scene_path,
        parent_path=params.parent_path,
        name=params.name,
        properties=params.properties,
    )
    return format_result(result, params.response_format)


async def handle_save_scene(client: GodotClient, params: SaveSceneInput) -> str:
    """Save the active scene."""
    result = await client.save_scene(scene_path=params.scene_path)
    return format_result(result, params.response_format)


async def handle_open_scene(client: GodotClient, params: OpenSceneInput) -> str:
    """Open a scene in the Godot Editor."""
    result = await client.open_scene(scene_path=params.scene_path)
    return format_result(result, params.response_format)


async def handle_create_scene(client: GodotClient, params: CreateSceneInput) -> str:
    """Create a brand new scene with its own dedicated root node."""
    result = await client.create_scene(
        scene_path=params.scene_path,
        root_type=params.root_type,
        root_name=params.root_name,
        properties=params.properties,
        open_in_editor=params.open_in_editor,
    )
    return format_result(result, params.response_format)
