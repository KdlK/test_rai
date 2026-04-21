"""Agent-facing skills for demonstrational text generation from walls."""

from __future__ import annotations

from typing import Any, Optional

from .model import create_wall, find_base_level
from .word_geometry import build_word_wall_segments, get_supported_word_builder_characters


def get_supported_wall_word_characters() -> dict[str, Any]:
    """Return the list of uppercase characters supported by the wall-word demo skill."""
    characters = get_supported_word_builder_characters()
    return {
        "characters": characters,
        "count": len(characters),
        "success": True,
    }


def preview_word_from_walls(
    text: str,
    start_x: float = 0.0,
    start_y: float = 0.0,
    letter_height: float = 3000.0,
    letter_spacing: float = 400.0,
    word_spacing: float = 900.0,
) -> dict[str, Any]:
    """Return the 2D wall segments for a demonstrational word without touching Renga."""
    segments = build_word_wall_segments(
        text,
        start_x=start_x,
        start_y=start_y,
        letter_height=letter_height,
        letter_spacing=letter_spacing,
        word_spacing=word_spacing,
    )
    return {
        "segment_count": len(segments),
        "segments": segments,
        "success": True,
        "text": text,
    }


def create_word_from_walls(
    text: str,
    level_id: Optional[int] = None,
    start_x: float = 0.0,
    start_y: float = 0.0,
    letter_height: float = 3000.0,
    letter_spacing: float = 400.0,
    word_spacing: float = 900.0,
    wall_thickness: float = 120.0,
    wall_height: float = 3000.0,
) -> dict[str, Any]:
    """Create a demonstrational word in Renga by composing multiple walls."""
    resolved_level_id = level_id if level_id is not None else find_base_level()
    if resolved_level_id is None:
        raise RuntimeError("Base level was not found. Provide level_id explicitly or create a base level.")

    segments = build_word_wall_segments(
        text,
        start_x=start_x,
        start_y=start_y,
        letter_height=letter_height,
        letter_spacing=letter_spacing,
        word_spacing=word_spacing,
    )

    created_walls: list[dict[str, Any]] = []
    wall_ids: list[int] = []
    for segment in segments:
        result = create_wall(
            level_id=int(resolved_level_id),
            start_x=segment["start"]["X"],
            start_y=segment["start"]["Y"],
            end_x=segment["end"]["X"],
            end_y=segment["end"]["Y"],
            thickness=wall_thickness,
            height=wall_height,
        )
        created_walls.append(
            {
                "char": segment["char"],
                "char_index": segment["char_index"],
                "segment_index": segment["segment_index"],
                "wall_id": result["wall_id"],
            }
        )
        wall_ids.append(int(result["wall_id"]))

    return {
        "created_walls": created_walls,
        "level_id": int(resolved_level_id),
        "segment_count": len(segments),
        "success": True,
        "text": text,
        "wall_height": float(wall_height),
        "wall_ids": wall_ids,
        "wall_thickness": float(wall_thickness),
    }
