import pytest

from qa_mcp import server


def test_generate_automation_rejects_invalid_test_case():

    with pytest.raises(
        ValueError,
        match="Invalid test case",
    ):
        server.generate_automation(
            test_case={
                "id": "TC001",
                "title": "Incomplete test case",
            }
        )