"""Pydantic models for Godot InputMap and project input actions."""

from enum import Enum

from pydantic import BaseModel, Field


class InputEventType(str, Enum):
    """Supported input event trigger types."""

    KEY = "key"
    MOUSE_BUTTON = "mouse_button"
    JOYPAD_BUTTON = "joypad_button"
    JOYPAD_MOTION = "joypad_motion"


class InputEventConfig(BaseModel):
    """Configuration for a single input event trigger."""

    type: InputEventType = Field(
        description="Type of input event ('key', 'mouse_button', 'joypad_button', 'joypad_motion').",
    )
    keycode: str | None = Field(
        default=None,
        description="Key name (e.g. 'Key.SPACE', 'Key.W', 'Key.ESCAPE', 'Key.ENTER') or string character.",
    )
    physical_keycode: str | None = Field(
        default=None,
        description="Physical keycode for layout-independent bindings.",
    )
    button_index: int | None = Field(
        default=None,
        description="Button index (Mouse: 1=Left, 2=Right, 3=Middle; Gamepad: 0=A/Cross, 1=B/Circle, etc.).",
    )
    axis: int | None = Field(
        default=None,
        description="Gamepad axis index (0=LeftStickX, 1=LeftStickY, 2=RightStickX, 3=RightStickY, etc.).",
    )
    axis_value: float | None = Field(
        default=None,
        description="Direction/threshold for axis motion (-1.0 or 1.0).",
    )


class GetInputActionsInput(BaseModel):
    """Input model for godot_get_input_actions."""

    filter_prefix: str | None = Field(
        default=None,
        description="Optional prefix to filter actions (e.g. 'ui_', 'player_').",
    )


class ConfigureInputActionInput(BaseModel):
    """Input model for godot_configure_input_action."""

    action_name: str = Field(
        description="Name of the input action (e.g. 'jump', 'move_forward', 'fire').",
    )
    deadzone: float = Field(
        default=0.5,
        description="Analog joystick deadzone threshold (0.0 to 1.0).",
    )
    events: list[InputEventConfig] = Field(
        default_factory=list,
        description="List of input events (keys, mouse buttons, gamepad buttons/axes) bound to this action.",
    )
    replace_existing: bool = Field(
        default=True,
        description="If true, clears previously bound events on this action before adding new ones.",
    )
    save_to_project_settings: bool = Field(
        default=True,
        description="If true, permanently saves the action configuration into project.godot.",
    )
