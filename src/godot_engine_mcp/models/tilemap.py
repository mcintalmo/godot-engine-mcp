"""Pydantic models for TileMapLayer cell painting and level design."""

from pydantic import BaseModel, Field


class TileCell(BaseModel):
    """Data for a single tile cell in a TileMapLayer."""

    coords: list[int] = Field(
        ...,
        description="Grid coordinate [x, y] of the cell to paint or query.",
    )
    source_id: int = Field(
        default=0,
        description="TileSet source ID (set to -1 to erase the cell).",
    )
    atlas_coords: list[int] = Field(
        default_factory=lambda: [0, 0],
        description="Atlas tile coordinate [col, row] in the tileset source texture.",
    )
    alternative_tile: int = Field(
        default=0,
        description="Alternative tile ID (for flipped, rotated, or variation tiles).",
    )


class SetTileMapCellsInput(BaseModel):
    """Input model for godot_set_tilemap_cells."""

    node_path: str = Field(
        ...,
        description="Target TileMapLayer or TileMap node path in the active scene (e.g. 'TileMapLayer' or 'World/Ground').",
    )
    cells: list[TileCell] = Field(
        ...,
        description="List of tile cells to paint or erase on the target layer.",
    )
    clear_before_paint: bool = Field(
        default=False,
        description="Whether to clear all existing cells on the layer before painting.",
    )


class GetTileMapCellsInput(BaseModel):
    """Input model for godot_get_tilemap_cells."""

    node_path: str = Field(
        ...,
        description="Target TileMapLayer or TileMap node path in the active scene.",
    )
    region: list[int] | None = Field(
        default=None,
        description="Optional bounding region [min_x, min_y, max_x, max_y] to filter queried cells.",
    )


class CreateTileMapLayerInput(BaseModel):
    """Input model for godot_create_tilemap_layer."""

    name: str = Field(
        default="TileMapLayer",
        description="Name of the TileMapLayer node to create.",
    )
    parent_node_path: str = Field(
        default=".",
        description="Target parent node path in the active scene (e.g. '.' or 'World').",
    )
    tile_set_path: str | None = Field(
        default=None,
        description="Optional path to a TileSet resource file (e.g. 'res://tilesets/ground.tres').",
    )
