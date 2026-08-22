"""Pydantic models for 'Playwright for Godot' Autonomous E2E Testing & UI Automation Engine."""

from typing import Any

from pydantic import BaseModel, Field


class FindElementsInput(BaseModel):
    """Input model for godot_find_elements."""

    selector_type: str = Field(
        default="text",
        description="Selector strategy: 'text' (matches button/label text), 'role' (e.g. 'Button', 'LineEdit'), 'type' (class name), 'name' (node name), 'group', 'property' (e.g. 'visible=true'), or 'path'.",
    )
    query: str = Field(
        description="Query value to search for based on selector_type (e.g. 'Start Game', 'Button', 'ScoreLabel', 'enemies').",
    )
    root_path: str | None = Field(
        default=None,
        description="Optional root node path to scope the search subtree (defaults to scene root).",
    )
    max_results: int = Field(
        default=50,
        description="Maximum number of matching elements to return.",
    )


class InteractNodeInput(BaseModel):
    """Input model for godot_interact_node."""

    node_path: str = Field(
        description="Path to the target node in the scene tree.",
    )
    action: str = Field(
        default="click",
        description="Interaction action: 'click', 'double_click', 'right_click', 'type_text', 'focus', 'hover', 'drag_and_drop', or 'scroll'.",
    )
    text: str | None = Field(
        default=None,
        description="Text content to type into the node (for 'type_text' action on LineEdit/TextEdit).",
    )
    clear_before_type: bool = Field(
        default=True,
        description="Whether to clear existing text before typing.",
    )
    drag_to_position: list[float] | None = Field(
        default=None,
        description="Target viewport position [x, y] to drag to (for 'drag_and_drop' action).",
    )
    scroll_delta: list[float] | None = Field(
        default=None,
        description="Scroll offset [dx, dy] (for 'scroll' action).",
    )


class WaitForConditionInput(BaseModel):
    """Input model for godot_wait_for_condition."""

    condition_type: str = Field(
        default="node_exists",
        description="Condition to evaluate: 'node_exists', 'node_visible', 'property_equals', or 'expression_true'.",
    )
    node_path: str | None = Field(
        default=None,
        description="Target node path for node-related conditions.",
    )
    property_name: str | None = Field(
        default=None,
        description="Property name to inspect for 'property_equals'.",
    )
    expected_value: Any = Field(
        default=None,
        description="Expected property value for 'property_equals'.",
    )
    expression: str | None = Field(
        default=None,
        description="GDScript boolean expression to evaluate for 'expression_true'.",
    )
    timeout_ms: int = Field(
        default=5000,
        description="Timeout in milliseconds before failing.",
    )
    poll_interval_ms: int = Field(
        default=100,
        description="Interval in milliseconds between condition checks.",
    )


class AssertNodeStateInput(BaseModel):
    """Input model for godot_assert_node_state."""

    node_path: str = Field(
        description="Path to the target node to assert state against.",
    )
    assertions: dict[str, Any] = Field(
        description="Dictionary of property names / condition keys and expected values (e.g. {'visible': True, 'text': 'Score: 100', 'disabled': False}).",
    )
