import base64
import json

import pytest

from qa_mcp.infrastructure.jira.cloud_client import (
    JiraCloudClient,
)


class FakeResponse:

    def __init__(
        self,
        payload: dict,
    ):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def read(self):
        return json.dumps(
            self.payload
        ).encode("utf-8")


class FakeOpener:

    def __init__(
        self,
        payload: dict,
    ):
        self.payload = payload
        self.request = None

    def __call__(
        self,
        request,
    ):
        self.request = request

        return FakeResponse(
            self.payload
        )


def issue_payload():

    return {
        "key": "QA-301",
        "fields": {
            "summary": (
                "Password reset fails"
            ),
            "description": (
                "User cannot reset "
                "password."
            ),
            "issuetype": {
                "name": "Bug"
            },
            "status": {
                "name": "Open"
            },
            "priority": {
                "name": "High"
            },
            "project": {
                "key": "QA",
                "name": "Customer Portal",
            },
            "assignee": {
                "displayName": "QA Engineer"
            },
            "reporter": {
                "displayName": "Product Owner"
            },
        },
    }


def test_cloud_client_get_issue():

    opener = FakeOpener(
        issue_payload()
    )

    client = JiraCloudClient(
        base_url=(
            "https://example.atlassian.net"
        ),
        email="qa@example.com",
        api_token="secret-token",
        opener=opener,
    )

    result = client.get_issue(
        "QA-301"
    )

    assert result.key == "QA-301"
    assert (
        result.summary
        == "Password reset fails"
    )
    assert result.issue_type == "Bug"
    assert result.status == "Open"
    assert result.priority == "High"
    assert result.project_key == "QA"
    assert (
        result.project_name
        == "Customer Portal"
    )
    assert (
        result.assignee
        == "QA Engineer"
    )
    assert (
        result.reporter
        == "Product Owner"
    )

    authorization = (
        opener.request
        .get_header("Authorization")
    )

    expected = base64.b64encode(
        b"qa@example.com:secret-token"
    ).decode("ascii")

    assert (
        authorization
        == f"Basic {expected}"
    )


def test_cloud_client_search():

    opener = FakeOpener(
        {
            "issues": [
                issue_payload()
            ],
            "nextPageToken": "ignored",
        }
    )

    client = JiraCloudClient(
        base_url=(
            "https://example.atlassian.net"
        ),
        email="qa@example.com",
        api_token="secret-token",
        opener=opener,
    )

    result = client.search_issues(
        "project = QA",
        max_results=10,
    )

    assert result.total == 1
    assert (
        result.issues[0].key
        == "QA-301"
    )


def test_cloud_client_rejects_missing_configuration():

    with pytest.raises(
        ValueError,
        match="Jira URL cannot be empty",
    ):

        JiraCloudClient(
            base_url="",
            email="qa@example.com",
            api_token="secret",
        )


def test_cloud_client_rejects_empty_issue_key():

    opener = FakeOpener(
        issue_payload()
    )

    client = JiraCloudClient(
        base_url=(
            "https://example.atlassian.net"
        ),
        email="qa@example.com",
        api_token="secret",
        opener=opener,
    )

    with pytest.raises(
        ValueError,
        match="issue key cannot be empty",
    ):

        client.get_issue("   ")


def test_cloud_client_rejects_empty_jql():

    opener = FakeOpener(
        {
            "issues": []
        }
    )

    client = JiraCloudClient(
        base_url=(
            "https://example.atlassian.net"
        ),
        email="qa@example.com",
        api_token="secret",
        opener=opener,
    )

    with pytest.raises(
        ValueError,
        match="Jira JQL cannot be empty",
    ):

        client.search_issues("   ")