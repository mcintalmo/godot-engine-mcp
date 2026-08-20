"""Pydantic models for Godot Theme and UI styling operations."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ThemeOverrideType(str, Enum):
    """Types of theme overrides applicable to Control nodes."""

    STYLEBOX = "stylebox"
    COLOR = "color"
    FONT = "font"
    FONT_SIZE = "font_size"
    CONSTANT = "constant"


class StyleBoxFlatConfig(BaseModel):
    """Configuration for a Godot StyleBoxFlat resource."""

    bg_color: str | None = Field(
        default=None,
        description="Background fill color in hex or named color (e.g. '#1e1e2e' or 'white').",
    )
    border_color: str | None = Field(
        default=None,
        description="Border outline color in hex or named color.",
    )
    border_width: int | None = Field(
        default=None,
        description="Uniform border width in pixels for all 4 edges.",
    )
    border_widths: list[int] | None = Field(
        default=None,
        description="Individual border widths as [left, top, right, bottom] in pixels.",
    )
    corner_radius: int | None = Field(
        default=None,
        description="Uniform corner radius in pixels for all 4 corners.",
    )
    corner_radii: list[int] | None = Field(
        default=None,
        description="Individual corner radii as [top_left, top_right, bottom_right, bottom_left] in pixels.",
    )
    content_margins: list[int] | None = Field(
        default=None,
        description="Padding margins as [left, top, right, bottom] in pixels.",
    )
    shadow_color: str | None = Field(
        default=None,
        description="Drop shadow color.",
    )
    shadow_size: int | None = Field(
        default=None,
        description="Drop shadow blur size in pixels.",
    )
    shadow_offset: list[float] | None = Field(
        default=None,
        description="Drop shadow offset as [x, y] in pixels.",
    )
    anti_aliasing: bool = Field(
        default=True,
        description="Whether antialiasing is enabled for borders and rounded corners.",
    )


class CreateThemeInput(BaseModel):
    """Input model for godot_create_theme."""

    save_path: str = Field(
        ...,
        description="Target path to save the Theme resource file (e.g. 'res://themes/dark_modern.tres').",
    )
    base_font_path: str | None = Field(
        default=None,
        description="Optional path to a default Font resource (.ttf, .otf, .tres).",
    )
    base_font_size: int | None = Field(
        default=None,
        description="Default font size in pixels.",
    )
    colors: dict[str, dict[str, str]] | None = Field(
        default=None,
        description="Type-grouped color overrides, e.g. {'Button': {'font_color': '#ffffff', 'font_hover_color': '#7aa2f7'}, 'Label': {'font_color': '#c0caf5'}}.",
    )
    constants: dict[str, dict[str, int]] | None = Field(
        default=None,
        description="Type-grouped integer constant overrides, e.g. {'VBoxContainer': {'separation': 12}, 'Button': {'outline_size': 2}}.",
    )
    styleboxes: dict[str, dict[str, StyleBoxFlatConfig]] | None = Field(
        default=None,
        description="Type-grouped StyleBoxFlat configurations, e.g. {'Button': {'normal': StyleBoxFlatConfig(...), 'hover': StyleBoxFlatConfig(...)}}.",
    )
    apply_to_node_path: str | None = Field(
        default=None,
        description="Optional Control node path in the active scene to assign the created theme to.",
    )


class ApplyThemeOverrideInput(BaseModel):
    """Input model for godot_apply_theme_override."""

    node_path: str = Field(
        ...,
        description="Target Control node path in the active scene (e.g. 'CanvasLayer/MainMenu/StartButton').",
    )
    override_type: ThemeOverrideType = Field(
        ...,
        description="Type of theme override: 'stylebox', 'color', 'font', 'font_size', or 'constant'.",
    )
    item_name: str = Field(
        ...,
        description="Theme item identifier (e.g. 'normal', 'hover', 'panel', 'font_color', 'separation').",
    )
    value: Any = Field(
        ...,
        description="Value to set: hex color string for 'color', integer for 'constant'/'font_size', font path for 'font', or StyleBoxFlatConfig dictionary for 'stylebox'.",
    )
