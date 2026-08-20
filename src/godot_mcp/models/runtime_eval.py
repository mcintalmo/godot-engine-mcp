"""Pydantic models for Godot runtime expression evaluation."""

from typing import Any

from pydantic import BaseModel, Field


class EvaluateExpressionInput(BaseModel):
    """Input model for godot_evaluate_expression."""

    expression: str = Field(
        description="GDScript expression to parse and evaluate (e.g. 'position.length()', 'get_child_count() > 0', '2 * PI * radius', 'get_total_score()').",
    )
    node_path: str | None = Field(
        default=None,
        description="Optional path of the context node in active scene to act as 'self'. Defaults to scene root.",
    )
    input_variables: dict[str, Any] | None = Field(
        default=None,
        description="Optional dictionary of input variables and values available inside the expression (e.g. {'radius': 5.0, 'multiplier': 2}).",
    )
