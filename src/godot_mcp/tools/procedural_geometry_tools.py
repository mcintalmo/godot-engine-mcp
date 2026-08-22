"""Tool handlers for Godot CSG Whiteboxing & Procedural Mesh Generation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.procedural_geometry import (
    CreateCSGShapeInput,
    GenerateProceduralMeshInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_create_csg_shape(
    client: GodotClient,
    params: CreateCSGShapeInput,
) -> str:
    """Handle godot_create_csg_shape tool execution."""
    result = await client.create_csg_shape(
        shape_type=params.shape_type,
        node_name=params.node_name,
        parent_path=params.parent_path,
        operation=params.operation,
        size=params.size,
        radius=params.radius,
        height=params.height,
        polygon_points=params.polygon_points,
        position=params.position,
        rotation_deg=params.rotation_deg,
        use_collision=params.use_collision,
        material_path=params.material_path,
    )
    return format_result(result)


async def handle_generate_procedural_mesh(
    client: GodotClient,
    params: GenerateProceduralMeshInput,
) -> str:
    """Handle godot_generate_procedural_mesh tool execution."""
    result = await client.generate_procedural_mesh(
        mesh_type=params.mesh_type,
        node_name=params.node_name,
        parent_path=params.parent_path,
        size=params.size,
        subdivisions=params.subdivisions,
        vertices=params.vertices,
        indices=params.indices,
        generate_normals=params.generate_normals,
        generate_tangents=params.generate_tangents,
        material_path=params.material_path,
        save_to_resource_path=params.save_to_resource_path,
    )
    return format_result(result)
