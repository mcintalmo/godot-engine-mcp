"""Pydantic models for Godot Interactive Runtime Input Simulation & Debug Drawing."""

from pydantic import BaseModel, Field


class SimulateInputInput(BaseModel):
    """Input model for godot_simulate_input."""

    event_type: str = Field(
        default="action",
        description="Type of input event: 'action', 'key', 'mouse_button', 'mouse_motion', 'joypad_button', or 'joypad_motion'.",
    )
    action: str | None = Field(
        default=None,
        description="Action name to trigger (e.g. 'ui_accept', 'jump', 'move_left').",
    )
    pressed: bool = Field(
        default=True,
        description="Whether the action/key/button is pressed (True) or released (False).",
    )
    strength: float = Field(
        default=1.0,
        description="Analog action/motion strength between 0.0 and 1.0.",
    )
    key: str | None = Field(
        default=None,
        description="Key name or code (e.g. 'W', 'Space', 'Escape', 'Enter').",
    )
    button_index: int = Field(
        default=1,
        description="Mouse button index (1: Left, 2: Right, 3: Middle, 4: WheelUp, 5: WheelDown).",
    )
    position: list[float] | None = Field(
        default=None,
        description="Viewport mouse position [x, y].",
    )
    relative: list[float] | None = Field(
        default=None,
        description="Relative mouse motion delta [dx, dy].",
    )


class DebugShape(BaseModel):
    """Specification for a single debug shape."""

    shape_type: str = Field(
        description="Shape type: 'line_3d', 'box_3d', 'sphere_3d', 'ray_3d', 'line_2d', 'rect_2d', 'circle_2d', 'text_label'.",
    )
    start: list[float] | None = Field(
        default=None,
        description="Start position for lines/rays (3D [x, y, z] or 2D [x, y]).",
    )
    end: list[float] | None = Field(
        default=None,
        description="End position for lines/rays.",
    )
    position: list[float] | None = Field(
        default=None,
        description="Center position for boxes/spheres/circles/text (3D [x, y, z] or 2D [x, y]).",
    )
    size: list[float] | None = Field(
        default=None,
        description="Box extents or rect dimensions (3D [x, y, z] or 2D [w, h]).",
    )
    radius: float | None = Field(
        default=None,
        description="Radius for spheres and circles.",
    )
    color: list[float] | str | None = Field(
        default=None,
        description="Shape color as [r, g, b, a] (0.0-1.0) or hex string (e.g. '#ff0000').",
    )
    duration: float = Field(
        default=5.0,
        description="Duration in seconds before the shape expires and is removed.",
    )
    text: str | None = Field(
        default=None,
        description="Text content for 'text_label' shapes.",
    )


class DrawDebugShapesInput(BaseModel):
    """Input model for godot_draw_debug_shapes."""

    shapes: list[DebugShape] = Field(
        description="List of debug shapes to render in the active scene or running game.",
    )


class ClearDebugShapesInput(BaseModel):
    """Input model for godot_clear_debug_shapes."""

    category: str | None = Field(
        default=None,
        description="Optional shape type/category filter to clear (e.g. '3d', '2d', or null for all).",
    )
