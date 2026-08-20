"""Pydantic models for Godot AudioServer bus and effect management."""

from typing import Any

from pydantic import BaseModel, Field


class GetAudioLayoutInput(BaseModel):
    """Input model for godot_get_audio_layout."""

    include_effects: bool = Field(
        default=True,
        description="Whether to include effect chain details for each audio bus.",
    )


class ConfigureAudioBusInput(BaseModel):
    """Input model for godot_configure_audio_bus."""

    bus_name: str = Field(
        ...,
        description="Audio bus name to create or configure (e.g. 'Master', 'Music', 'SFX', 'Voice', 'Ambience').",
    )
    create_if_missing: bool = Field(
        default=True,
        description="Whether to create the bus if it does not already exist in the AudioServer layout.",
    )
    volume_db: float | None = Field(
        default=None,
        description="Volume in decibels (0.0 = unity gain, -80.0 = silent). Mutually exclusive with volume_linear.",
    )
    volume_linear: float | None = Field(
        default=None,
        description="Volume as a linear scalar 0.0 to 1.0 (converted automatically to dB).",
    )
    send_to_bus: str | None = Field(
        default=None,
        description="Target destination bus name for audio routing (e.g. 'Master').",
    )
    mute: bool | None = Field(
        default=None,
        description="Whether the audio bus is muted.",
    )
    solo: bool | None = Field(
        default=None,
        description="Whether the audio bus is in solo mode.",
    )
    bypass_effects: bool | None = Field(
        default=None,
        description="Whether to bypass all effect processing on this bus.",
    )
    save_layout_path: str | None = Field(
        default=None,
        description="Optional path to save the updated AudioBusLayout resource (e.g. 'res://default_bus_layout.tres').",
    )


class SetBusEffectInput(BaseModel):
    """Input model for godot_set_bus_effect."""

    bus_name: str = Field(
        ...,
        description="Target audio bus name (e.g. 'Master', 'Music', 'SFX').",
    )
    effect_type: str = Field(
        ...,
        description="Class name of the AudioEffect resource (e.g. 'AudioEffectReverb', 'AudioEffectChorus', 'AudioEffectDelay', 'AudioEffectLowPassFilter', 'AudioEffectCompressor', 'AudioEffectLimiter', 'AudioEffectEQ', 'AudioEffectPitchShift').",
    )
    effect_index: int | None = Field(
        default=None,
        description="Optional effect slot index on the bus (0-indexed). If None, appends the effect to the end of the bus chain.",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the audio effect is enabled.",
    )
    properties: dict[str, Any] | None = Field(
        default=None,
        description="Effect property overrides (e.g. {'room_size': 0.7, 'wet': 0.35, 'cutoff_hz': 2000.0}).",
    )
    save_layout_path: str | None = Field(
        default=None,
        description="Optional path to save the updated AudioBusLayout resource (e.g. 'res://default_bus_layout.tres').",
    )
