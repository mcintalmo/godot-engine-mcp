"""Pydantic models for Godot Editor Undo/Redo operations."""

from pydantic import BaseModel, Field


class UndoInput(BaseModel):
    """Input model for godot_undo."""

    history_id: int | None = Field(
        default=None,
        description="Optional history ID to undo on (defaults to currently edited scene undo history).",
    )


class RedoInput(BaseModel):
    """Input model for godot_redo."""

    history_id: int | None = Field(
        default=None,
        description="Optional history ID to redo on (defaults to currently edited scene undo history).",
    )
