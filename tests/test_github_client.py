from abc import ABC

from qa_mcp.infrastructure.github.client import (
    GitHubClient,
)


def test_github_client_is_abstract():

    assert issubclass(
        GitHubClient,
        ABC,
    )


def test_github_client_defines_read_only_operations():

    expected_methods = {
        "get_repository",
        "get_issue",
        "get_pull_request",
        "search_issues",
    }

    actual_methods = {
        name
        for name in dir(GitHubClient)
        if not name.startswith("_")
    }

    assert expected_methods.issubset(
        actual_methods
    )