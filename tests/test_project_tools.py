import uuid

from qa_mcp.server import (
    create_qa_project,
    get_qa_project,
)


def unique_project_id() -> str:
    return f"tool-test-{uuid.uuid4().hex}"


def test_create_qa_project_tool():

    project_id = unique_project_id()

    result = create_qa_project(
        project_id=project_id,
        name="Tool Test Project",
        application="Customer Portal",
        environment="QA",
    )

    assert result["project_id"] == project_id

    assert result["name"] == (
        "Tool Test Project"
    )

    assert result["application"] == (
        "Customer Portal"
    )


def test_get_qa_project_tool():

    project_id = unique_project_id()

    create_qa_project(
        project_id=project_id,
        name="Tool Test Project",
        application="Customer Portal",
        environment="QA",
    )

    result = get_qa_project(
        project_id
    )

    assert result["project_id"] == project_id

    assert result["environment"] == (
        "QA"
    )