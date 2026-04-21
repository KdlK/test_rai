"""Geometry helpers for building words from wall segments."""

from __future__ import annotations

from typing import Any

_RUSSIAN_ALPHABET = list(
    "\u0410\u0411\u0412\u0413\u0414\u0415\u0401\u0416\u0417\u0418\u0419\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424\u0425\u0426\u0427\u0428\u0429\u042a\u042b\u042c\u042d\u042e\u042f"
)

_GLYPHS: dict[str, dict[str, Any]] = {
    "\u0410": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.5, 1.0)),
            ((0.5, 1.0), (1.0, 0.0)),
            ((0.2, 0.45), (0.8, 0.45)),
        ],
    },
    "\u0411": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.0, 0.5), (0.8, 0.5)),
            ((0.0, 0.0), (0.8, 0.0)),
            ((0.8, 0.0), (0.8, 0.5)),
        ],
    },
    "\u0412": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (0.8, 1.0)),
            ((0.8, 0.5), (0.8, 1.0)),
            ((0.0, 0.5), (0.8, 0.5)),
            ((0.0, 0.0), (0.8, 0.0)),
            ((0.8, 0.0), (0.8, 0.5)),
        ],
    },
    "\u0413": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
        ],
    },
    "\u0414": {
        "width": 1.1,
        "segments": [
            ((0.0, 0.0), (1.1, 0.0)),
            ((0.15, 0.0), (0.15, 0.9)),
            ((0.95, 0.0), (0.95, 0.9)),
            ((0.15, 0.9), (0.95, 0.9)),
        ],
    },
    "\u0415": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.0, 0.5), (0.7, 0.5)),
            ((0.0, 0.0), (1.0, 0.0)),
        ],
    },
    "\u0401": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.0, 0.5), (0.7, 0.5)),
            ((0.0, 0.0), (1.0, 0.0)),
            ((0.2, 1.15), (0.2, 1.25)),
            ((0.8, 1.15), (0.8, 1.25)),
        ],
    },
    "\u0416": {
        "width": 1.4,
        "segments": [
            ((0.0, 0.0), (0.7, 0.5)),
            ((0.0, 1.0), (0.7, 0.5)),
            ((0.7, 0.0), (0.7, 1.0)),
            ((1.4, 0.0), (0.7, 0.5)),
            ((1.4, 1.0), (0.7, 0.5)),
        ],
    },
    "\u0417": {
        "width": 1.0,
        "segments": [
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.35, 0.5), (1.0, 0.5)),
            ((0.0, 0.0), (1.0, 0.0)),
            ((1.0, 0.5), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 0.5)),
        ],
    },
    "\u0418": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
        ],
    },
    "\u0419": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
            ((0.25, 1.15), (0.5, 1.3)),
            ((0.5, 1.3), (0.75, 1.15)),
        ],
    },
    "\u041a": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.5), (1.0, 1.0)),
            ((0.0, 0.5), (1.0, 0.0)),
        ],
    },
    "\u041b": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.5, 1.0)),
            ((0.5, 1.0), (1.0, 0.0)),
        ],
    },
    "\u041c": {
        "width": 1.2,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (0.6, 0.0)),
            ((0.6, 0.0), (1.2, 1.0)),
            ((1.2, 0.0), (1.2, 1.0)),
        ],
    },
    "\u041d": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
            ((0.0, 0.5), (1.0, 0.5)),
        ],
    },
    "\u041e": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
            ((0.0, 0.0), (1.0, 0.0)),
        ],
    },
    "\u041f": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
        ],
    },
    "\u0420": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (0.9, 1.0)),
            ((0.9, 0.5), (0.9, 1.0)),
            ((0.0, 0.5), (0.9, 0.5)),
        ],
    },
    "\u0421": {
        "width": 1.0,
        "segments": [
            ((1.0, 1.0), (0.0, 1.0)),
            ((0.0, 1.0), (0.0, 0.0)),
            ((0.0, 0.0), (1.0, 0.0)),
        ],
    },
    "\u0422": {
        "width": 1.0,
        "segments": [
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.5, 0.0), (0.5, 1.0)),
        ],
    },
    "\u0423": {
        "width": 1.0,
        "segments": [
            ((0.0, 1.0), (0.5, 0.5)),
            ((1.0, 1.0), (0.5, 0.5)),
            ((0.5, 0.5), (0.5, 0.0)),
        ],
    },
    "\u0424": {
        "width": 1.2,
        "segments": [
            ((0.0, 0.2), (0.0, 0.8)),
            ((0.0, 0.8), (1.2, 0.8)),
            ((1.2, 0.2), (1.2, 0.8)),
            ((0.0, 0.2), (1.2, 0.2)),
            ((0.6, 0.0), (0.6, 1.0)),
        ],
    },
    "\u0425": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (1.0, 1.0)),
            ((0.0, 1.0), (1.0, 0.0)),
        ],
    },
    "\u0426": {
        "width": 1.1,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 1.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
            ((1.0, 0.0), (1.0, -0.2)),
        ],
    },
    "\u0427": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.5), (0.0, 1.0)),
            ((1.0, 0.0), (1.0, 1.0)),
            ((0.0, 0.5), (1.0, 0.5)),
        ],
    },
    "\u0428": {
        "width": 1.4,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.7, 0.0), (0.7, 1.0)),
            ((1.4, 0.0), (1.4, 1.0)),
            ((0.0, 0.0), (1.4, 0.0)),
        ],
    },
    "\u0429": {
        "width": 1.5,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.7, 0.0), (0.7, 1.0)),
            ((1.4, 0.0), (1.4, 1.0)),
            ((0.0, 0.0), (1.4, 0.0)),
            ((1.4, 0.0), (1.4, -0.2)),
        ],
    },
    "\u042a": {
        "width": 1.2,
        "segments": [
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.35, 0.0), (0.35, 1.0)),
            ((0.35, 0.0), (1.0, 0.0)),
            ((0.35, 0.5), (1.0, 0.5)),
            ((1.0, 0.0), (1.0, 0.5)),
        ],
    },
    "\u042b": {
        "width": 1.5,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.0), (0.7, 0.0)),
            ((0.0, 0.5), (0.7, 0.5)),
            ((0.7, 0.0), (0.7, 0.5)),
            ((1.5, 0.0), (1.5, 1.0)),
        ],
    },
    "\u042c": {
        "width": 1.0,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.0), (0.8, 0.0)),
            ((0.0, 0.5), (0.8, 0.5)),
            ((0.8, 0.0), (0.8, 0.5)),
        ],
    },
    "\u042d": {
        "width": 1.0,
        "segments": [
            ((0.0, 1.0), (1.0, 1.0)),
            ((0.4, 0.5), (1.0, 0.5)),
            ((0.0, 0.0), (1.0, 0.0)),
            ((1.0, 0.0), (1.0, 1.0)),
        ],
    },
    "\u042e": {
        "width": 1.25,
        "segments": [
            ((0.0, 0.0), (0.0, 1.0)),
            ((0.0, 0.5), (0.35, 0.5)),
            ((0.35, 0.0), (0.35, 1.0)),
            ((0.35, 1.0), (1.25, 1.0)),
            ((1.25, 0.0), (1.25, 1.0)),
            ((0.35, 0.0), (1.25, 0.0)),
        ],
    },
    "\u042f": {
        "width": 1.0,
        "segments": [
            ((1.0, 0.0), (1.0, 1.0)),
            ((0.1, 1.0), (1.0, 1.0)),
            ((0.1, 0.5), (1.0, 0.5)),
            ((0.1, 0.5), (0.1, 1.0)),
            ((0.1, 0.5), (1.0, 0.0)),
        ],
    },
}


def get_supported_word_builder_characters() -> list[str]:
    """Return supported uppercase characters for wall-word generation."""
    return [char for char in _RUSSIAN_ALPHABET if char in _GLYPHS]


def build_word_wall_segments(
    text: str,
    *,
    start_x: float = 0.0,
    start_y: float = 0.0,
    letter_height: float = 3000.0,
    letter_spacing: float = 400.0,
    word_spacing: float = 900.0,
) -> list[dict[str, Any]]:
    """Build 2D wall segments for a word using a simple uppercase stroke font."""
    normalized_text = text.strip().upper()
    if not normalized_text:
        raise ValueError("Text must be a non-empty string.")
    if letter_height <= 0:
        raise ValueError("letter_height must be positive.")
    if letter_spacing < 0 or word_spacing < 0:
        raise ValueError("letter_spacing and word_spacing must be non-negative.")

    cursor_x = float(start_x)
    base_y = float(start_y)
    scale = float(letter_height)
    segments: list[dict[str, Any]] = []
    unsupported: list[str] = []

    for char_index, char in enumerate(normalized_text):
        if char == " ":
            cursor_x += word_spacing
            continue

        glyph = _GLYPHS.get(char)
        if glyph is None:
            unsupported.append(char)
            continue

        for segment_index, ((x1, y1), (x2, y2)) in enumerate(glyph["segments"]):
            segments.append(
                {
                    "char": char,
                    "char_index": char_index,
                    "segment_index": segment_index,
                    "start": {
                        "X": cursor_x + float(x1) * scale,
                        "Y": base_y + float(y1) * scale,
                    },
                    "end": {
                        "X": cursor_x + float(x2) * scale,
                        "Y": base_y + float(y2) * scale,
                    },
                }
            )

        cursor_x += float(glyph["width"]) * scale + float(letter_spacing)

    if unsupported:
        unique_unsupported = ", ".join(sorted(set(unsupported)))
        raise ValueError(
            f"Unsupported characters for wall-word generation: {unique_unsupported}. "
            f"Supported characters: {' '.join(get_supported_word_builder_characters())}"
        )

    return segments
