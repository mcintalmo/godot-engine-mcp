"""Unit tests for Pydantic input models and formatters."""

import pytest
from pydantic import ValidationError

from godot_engine_mcp.models.common import EngineMode, ResponseFormat, StandardResult
from godot_engine_mcp.models.scene import (
    ConnectSignalInput,
    CreateNodeInput,
    ModifyNodeInput,
)
from godot_engine_mcp.tools.formatters import format_result


def test_create_node_input_validation() -> None:
    """Test CreateNodeInput validation constraints."""
    inp = CreateNodeInput(
        type_name="Sprite2D",
        name="PlayerSprite",
        parent_path=".",
        properties={"position": [10, 20]},
    )
    assert inp.type_name == "Sprite2D"
    assert inp.name == "PlayerSprite"
    assert inp.parent_path == "."
    assert inp.response_format == ResponseFormat.MARKDOWN

    # Empty name should fail
    with pytest.raises(ValidationError):
        CreateNodeInput(type_name="Sprite2D", name="")


def test_modify_node_input_validation() -> None:
    """Test ModifyNodeInput validation."""
    inp = ModifyNodeInput(node_path="Player", properties={"visible": False})
    assert inp.node_path == "Player"
    assert inp.properties == {"visible": False}

    # Empty properties dict should fail
    with pytest.raises(ValidationError):
        ModifyNodeInput(node_path="Player", properties={})


def test_connect_signal_input() -> None:
    """Test ConnectSignalInput validation."""
    inp = ConnectSignalInput(
        source_node_path="Button",
        signal_name="pressed",
        target_node_path="Player",
        method_name="_on_button_pressed",
    )
    assert inp.signal_name == "pressed"
    assert inp.flags == 0


def test_format_result_markdown() -> None:
    """Test formatting StandardResult into markdown."""
    res = StandardResult(
        success=True,
        message="Created node successfully",
        mode=EngineMode.LIVE_EDITOR,
        data={"node_path": "Player/Sprite2D"},
    )
    md = format_result(res, ResponseFormat.MARKDOWN)
    assert "### Godot Operation [SUCCESS]" in md
    assert "Created node successfully" in md
    assert "Player/Sprite2D" in md


def test_format_result_json() -> None:
    """Test formatting StandardResult into JSON."""
    res = StandardResult(
        success=False,
        message="Node not found",
        mode=EngineMode.HEADLESS_CLI,
        error_code="NOT_FOUND",
        actionable_hint="Check scene path",
    )
    json_out = format_result(res, ResponseFormat.JSON)
    assert '"success": false' in json_out
    assert '"error_code": "NOT_FOUND"' in json_out
    assert '"actionable_hint": "Check scene path"' in json_out
