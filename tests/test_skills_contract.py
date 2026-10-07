from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_FILE = ROOT / "skills.md"
SERVER_FILE = ROOT / "src" / "qa_mcp" / "server.py"


def _skills_text() -> str:
    return SKILLS_FILE.read_text(encoding="utf-8")


def _mcp_tool_names() -> set[str]:
    tree = ast.parse(SERVER_FILE.read_text(encoding="utf-8"))
    names: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "tool"
            ):
                names.add(node.name)

    return names


def _active_skill_sections() -> list[tuple[str, str]]:
    text = _skills_text()

    matches = list(
        re.finditer(
            r"^## Skill: ([A-Za-z0-9_]+)\s*$",
            text,
            re.MULTILINE,
        )
    )

    sections: list[tuple[str, str]] = []

    for index, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]

        if re.search(r"^ACTIVE\s*$", body, re.MULTILINE):
            sections.append((name, body))

    return sections


def _declared_tool_name(body: str) -> str | None:
    match = re.search(
        r"^`([A-Za-z0-9_]+)`\s*$",
        body,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def test_skills_contract_exists() -> None:
    text = _skills_text()

    assert SKILLS_FILE.exists()
    assert "# QA MCP Agent Skills Contract" in text
    assert "# 3. Skill Status" in text
    assert "# 4. Active Skills" in text
    assert "# 5. Skills Explicitly Not Active Yet" in text


def test_active_skills_map_to_existing_mcp_tools() -> None:
    active_sections = _active_skill_sections()
    mcp_tools = _mcp_tool_names()

    assert active_sections

    declared_tools: list[str] = []

    for skill_name, body in active_sections:
        tool_name = _declared_tool_name(body)

        assert tool_name is not None, (
            f"ACTIVE skill '{skill_name}' does not declare an MCP tool."
        )

        assert tool_name in mcp_tools, (
            f"ACTIVE skill '{skill_name}' maps to missing MCP tool "
            f"'{tool_name}'."
        )

        declared_tools.append(tool_name)

    assert len(declared_tools) == len(set(declared_tools))


def test_contract_does_not_activate_design_only_capabilities() -> None:
    content = _skills_text()

    automation_validation = re.search(
        r"(?ms)^## Automation Validation\n.*?(?=\n## |\n# |\Z)",
        content,
    )

    assert automation_validation is not None
    assert "DESIGN_ONLY" in automation_validation.group(0)

    scenario_batching = re.search(
        r"(?ms)^## Scenario-Batched Test Generation\n.*?(?=\n## |\n# |\Z)",
        content,
    )

    assert scenario_batching is not None
    assert "DESIGN_ONLY" in scenario_batching.group(0)


def test_contract_preserves_execution_safety_boundary() -> None:
    content = _skills_text()

    execution_section = re.search(
        r"(?ms)^## Skill: execute_automation_code\n.*?(?=\n## Skill: |\n# |\Z)",
        content,
    )

    assert execution_section is not None

    body = execution_section.group(0)

    assert "AutomationExecutionService" in body
    assert "arbitrary shell commands" in body
    assert "workspace isolation" in body
    assert "execution timeout" in body


def test_contract_requires_traceability() -> None:
    content = _skills_text()

    required_terms = [
        "Requirement",
        "Test Cases",
        "Suite Version",
        "Automation Candidate",
        "Automation Case",
        "Automation Artifact",
        "Execution Result",
        "Failure Analysis",
    ]

    for term in required_terms:
        assert term in content


def test_contract_does_not_claim_unimplemented_autonomy() -> None:
    content = _skills_text()

    expected = {
        "## Autonomous QA Orchestration": "NOT_IMPLEMENTED",
        "## Autonomous Retry / Self-Healing": "NOT_IMPLEMENTED",
        "## CI/CD Triggering": "NOT_IMPLEMENTED",
    }

    for heading, status in expected.items():
        section = re.search(
            rf"(?ms)^{re.escape(heading)}\n.*?(?=\n## |\n# |\Z)",
            content,
        )

        assert section is not None, f"Missing section: {heading}"
        assert status in section.group(0)
