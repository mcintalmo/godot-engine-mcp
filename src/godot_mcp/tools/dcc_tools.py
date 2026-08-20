"""Tool handlers for DCC / Blender 3D model import and instancing."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.dcc_asset import (
    ConfigureGLTFImportInput,
    InstantiateModelInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_instantiate_model(
    client: GodotClient,
    params: InstantiateModelInput,
) -> str:
    """Handle godot_instantiate_model tool execution."""
    result = await client.instantiate_model(
        source_path=params.source_path,
        parent_path=params.parent_path,
        node_name=params.node_name,
        position=params.position,
        rotation=params.rotation,
        scale=params.scale,
        collision_mode=params.collision_mode.value,
        save_as_scene_path=params.save_as_scene_path,
    )
    return format_result(result)


async def handle_configure_gltf_import(
    client: GodotClient,
    params: ConfigureGLTFImportInput,
) -> str:
    """Handle godot_configure_gltf_import tool execution."""
    result = await client.configure_gltf_import(
        model_path=params.model_path,
        import_as_skeleton_bones=params.import_as_skeleton_bones,
        generate_lods=params.generate_lods,
        lod_threshold=params.lod_threshold,
        generate_shadow_mesh=params.generate_shadow_mesh,
        extract_materials=params.extract_materials,
        reimport=params.reimport,
    )
    return format_result(result)
