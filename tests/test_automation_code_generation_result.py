from qa_mcp.models.schemas import GeneratedAutomationArtifact


def test_generated_automation_artifact_contains_code_generation_metadata():

    artifact = GeneratedAutomationArtifact(
        id="GA001",
        automation_case_id="AC001",
        framework="Playwright",
        language="Python",
        file_name="test_successful_login.py",
        code="def test_successful_login():\n    pass",
    )

    assert artifact.id == "GA001"
    assert artifact.automation_case_id == "AC001"
    assert artifact.framework == "Playwright"
    assert artifact.language == "Python"
    assert artifact.file_name == "test_successful_login.py"
    assert "def test_successful_login" in artifact.code