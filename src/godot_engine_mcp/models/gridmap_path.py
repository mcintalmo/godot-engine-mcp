"""Pydantic models for Godot 3D GridMaps & Procedural Bezier Paths."""

from pydantic import BaseModel, Field


class GridMapCell(BaseModel):
    """Specification of a single voxel cell on a GridMap."""

    position: list[int] = Field(
        description="3D integer coordinates of the cell [x, y, z].",
    )
    item_id: int = Field(
        default=0,
        description="MeshLibrary item index to place (or -1 to clear).",
    )
    orientation: int = Field(
        default=0,
        description="Orthogonal rotation basis index (0-23) for tile orientation.",
    )


class ConfigureGridMapInput(BaseModel):
    """Input model for godot_configure_gridmap."""

    gridmap_node_path: str = Field(
        description="Path to the GridMap node in the active scene.",
    )
    mesh_library_path: str | None = Field(
        default=None,
        description="Optional path to assign a MeshLibrary resource (e.g. 'res://assets/tiles.meshlib').",
    )
    cell_size: list[float] | None = Field(
        default=None,
        description="GridMap cell size in 3D units [sx, sy, sz] (e.g. [2.0, 2.0, 2.0]).",
    )
    cells_to_set: list[GridMapCell] | None = Field(
        default=None,
        description="List of voxel cells to place or update on the GridMap.",
    )
    cells_to_clear: list[list[int]] | None = Field(
        default=None,
        description="List of cell coordinates [[x, y, z], ...] to erase.",
    )
    clear_all: bool = Field(
        default=False,
        description="Whether to clear all existing cells from the GridMap.",
    )
    collision_layer: int | None = Field(
        default=None,
        description="Collision layer bitmask for the GridMap.",
    )
    collision_mask: int | None = Field(
        default=None,
        description="Collision mask bitmask for the GridMap.",
    )


class CurvePoint(BaseModel):
    """Specification of a control point on a 2D or 3D Bezier curve."""

    position: list[float] = Field(
        description="Control point position (3D [x, y, z] or 2D [x, y]).",
    )
    in_handle: list[float] | None = Field(
        default=None,
        description="In tangent vector handle (relative offset from point position).",
    )
    out_handle: list[float] | None = Field(
        default=None,
        description="Out tangent vector handle (relative offset from point position).",
    )
    tilt: float = Field(
        default=0.0,
        description="Tilt angle in radians (for 3D curves).",
    )


class CreateCurvePathInput(BaseModel):
    """Input model for godot_create_curve_path."""

    path_type: str = Field(
        default="3d",
        description="Path dimension: '3d' (Path3D / Curve3D) or '2d' (Path2D / Curve2D).",
    )
    node_name: str = Field(
        default="Path3D",
        description="Name of the new Path node to create.",
    )
    parent_path: str = Field(
        default=".",
        description="Parent node path in the active scene to attach the Path to.",
    )
    points: list[CurvePoint] = Field(
        description="List of curve control points with optional Bezier handles and tilt.",
    )
    closed: bool = Field(
        default=False,
        description="Whether the curve is a closed continuous loop.",
    )
    add_path_follow: bool = Field(
        default=False,
        description="Whether to automatically attach a child PathFollow3D / PathFollow2D node.",
    )
    path_follow_name: str = Field(
        default="PathFollow",
        description="Name of the child PathFollow node if add_path_follow is true.",
    )
