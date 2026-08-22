"""Pydantic models for Godot CSG Whiteboxing & Procedural Mesh Generation."""

from pydantic import BaseModel, Field


class CreateCSGShapeInput(BaseModel):
    """Input model for godot_create_csg_shape."""

    shape_type: str = Field(
        default="box",
        description="CSG shape type: 'box', 'cylinder', 'sphere', 'polygon', 'torus', or 'combiner'.",
    )
    node_name: str = Field(
        default="CSGShape",
        description="Name of the new CSG node in the scene tree.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene to attach the CSG node to.",
    )
    operation: str = Field(
        default="union",
        description="CSG boolean operation: 'union', 'intersection', or 'subtraction'.",
    )
    size: list[float] | None = Field(
        default=None,
        description="3D dimensions [sx, sy, sz] for box or dimensions for polygon extrude.",
    )
    radius: float | None = Field(
        default=None,
        description="Radius for sphere, cylinder, or torus.",
    )
    height: float | None = Field(
        default=None,
        description="Height for cylinder.",
    )
    polygon_points: list[list[float]] | None = Field(
        default=None,
        description="2D polygon points [[x, y], ...] for CSGPolygon3D.",
    )
    position: list[float] | None = Field(
        default=None,
        description="Local 3D position [x, y, z] of the CSG node.",
    )
    rotation_deg: list[float] | None = Field(
        default=None,
        description="Local 3D Euler rotation [rx, ry, rz] in degrees.",
    )
    use_collision: bool = Field(
        default=True,
        description="Whether the root CSG shape creates physics collisions.",
    )
    material_path: str | None = Field(
        default=None,
        description="Optional material resource path (e.g. 'res://materials/wall.tres').",
    )


class GenerateProceduralMeshInput(BaseModel):
    """Input model for godot_generate_procedural_mesh."""

    mesh_type: str = Field(
        default="grid",
        description="Procedural mesh type: 'grid', 'prism', 'pyramid', or 'custom_vertices'.",
    )
    node_name: str = Field(
        default="ProceduralMesh",
        description="Name of the new MeshInstance3D node to create.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene.",
    )
    size: list[float] | None = Field(
        default=None,
        description="Size dimensions (e.g. [10.0, 10.0] for grid, [2.0, 3.0, 2.0] for prism/pyramid).",
    )
    subdivisions: list[int] | None = Field(
        default=None,
        description="Subdivisions [nx, nz] for grid meshes (e.g. [16, 16]).",
    )
    vertices: list[list[float]] | None = Field(
        default=None,
        description="List of 3D vertex positions [[x, y, z], ...] for custom mesh generation.",
    )
    indices: list[int] | None = Field(
        default=None,
        description="List of triangle indices for custom vertex generation.",
    )
    generate_normals: bool = Field(
        default=True,
        description="Whether to generate smooth normals with SurfaceTool.",
    )
    generate_tangents: bool = Field(
        default=True,
        description="Whether to generate tangent vectors for normal mapping.",
    )
    material_path: str | None = Field(
        default=None,
        description="Optional material resource path to apply to the mesh.",
    )
    save_to_resource_path: str | None = Field(
        default=None,
        description="Optional resource path to save the generated ArrayMesh as an asset (e.g. 'res://models/terrain.tres').",
    )
