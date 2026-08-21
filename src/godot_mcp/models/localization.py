"""Pydantic models for Godot Internationalization & Translation management."""

from pydantic import BaseModel, Field


class GetTranslationsInput(BaseModel):
    """Input model for godot_get_translations."""

    locale_filter: str | None = Field(
        default=None,
        description="Optional language/locale code filter (e.g. 'en', 'es', 'fr', 'ja').",
    )


class AddTranslationInput(BaseModel):
    """Input model for godot_add_translation."""

    translation_path: str = Field(
        description="Path to the translation resource or table file (e.g. 'res://localization/strings.csv', 'res://translations/game.en.translation').",
    )
    test_locale: str | None = Field(
        default=None,
        description="Optional locale to switch to via TranslationServer (e.g. 'es', 'de').",
    )
