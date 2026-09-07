from __future__ import annotations

import json
from typing import Any


def parse_json_response(raw_response: str) -> Any:
    """Parse JSON returned by an LLM, tolerating common formatting wrappers."""

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

    if len(lines) >= 2:
        first = lines[0].strip().lower()
        last = lines[-1].strip()

        if first in {"```", "```json"} and last == "```":
            text = "\n".join(lines[1:-1]).strip()

    # First try the complete response as JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        original_error = exc

    # Bedrock models may occasionally return explanatory text
    # before or after an otherwise valid JSON object/array.
    decoder = json.JSONDecoder()

    for index, character in enumerate(text):
        if character not in "[{":
            continue

        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue

        remainder = text[index + end:].strip()

        # Valid JSON may be surrounded by explanatory prose.
        # The JSON itself must still be completely decodable.
        return value

    raise original_error
