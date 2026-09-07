from __future__ import annotations

import json
from typing import Any


def parse_json_response(raw_response: str) -> Any:
    """Parse an LLM JSON response while tolerating safe formatting wrappers."""

    if not isinstance(raw_response, str):
        raise TypeError("LLM response must be a string")

    text = raw_response.strip()

    if not text:
        raise json.JSONDecodeError(
            "Empty LLM response",
            raw_response,
            0,
        )

    # LLMs commonly wrap valid JSON in Markdown code fences.
    lines = text.splitlines()

    if (
        len(lines) >= 2
        and lines[0].strip().lower() in {"```", "```json"}
        and lines[-1].strip() == "```"
    ):
        text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError as original_error:
        # Allow short explanatory text before/after one clearly decodable
        # JSON object/array, but never attempt to repair malformed JSON.
        decoder = json.JSONDecoder()

        for index, character in enumerate(text):
            if character not in "[{":
                continue

            try:
                value, _ = decoder.raw_decode(text[index:])
                return value
            except json.JSONDecodeError:
                continue

        raise original_error
