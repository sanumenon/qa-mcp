from abc import ABC

from qa_mcp.infrastructure.slack.client import (
    SlackClient,
)


def test_slack_client_is_abstract():

    assert issubclass(
        SlackClient,
        ABC,
    )


def test_slack_client_defines_read_only_operations():

    expected_methods = {
        "get_channel",
        "get_messages",
        "search_messages",
        "get_thread",
    }

    actual_methods = {
        name
        for name in dir(SlackClient)
        if not name.startswith("_")
    }

    assert expected_methods.issubset(
        actual_methods
    )