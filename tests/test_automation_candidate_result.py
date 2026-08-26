from qa_mcp.models.schemas import (
    AutomationCandidateResult,
)


def test_automation_candidate_result_contains_counts():

    result = AutomationCandidateResult(
        candidate_ids=[
            "TC001",
            "TC002",
        ],
        manual_ids=[
            "TC003",
        ],
        total=3,
    )

    assert result.candidate_ids == [
        "TC001",
        "TC002",
    ]

    assert result.manual_ids == [
        "TC003",
    ]

    assert result.total == 3