import json

import pytest

from qa_mcp.core.json_response import parse_json_response


def test_parse_plain_json():
    assert parse_json_response('{"summary": "Login"}') == {
        "summary": "Login"
    }


def test_parse_json_code_fence():
    assert parse_json_response(
        '```json\n{"summary": "Login"}\n```'
    ) == {
        "summary": "Login"
    }


def test_parse_json_code_fence_without_language():
    assert parse_json_response(
        '```\n{"summary": "Login"}\n```'
    ) == {
        "summary": "Login"
    }


def test_parse_json_with_surrounding_text():
    assert parse_json_response(
        'Here is the analysis:\n{"summary": "Login"}\nDone.'
    ) == {
        "summary": "Login"
    }


def test_parse_malformed_json_still_fails():
    with pytest.raises(json.JSONDecodeError):
        parse_json_response('{"summary": "Login"')


def test_parse_empty_response_fails():
    with pytest.raises(json.JSONDecodeError):
        parse_json_response("")
