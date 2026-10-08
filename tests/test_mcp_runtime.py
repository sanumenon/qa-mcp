from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def test_launched_mcp_process_discovers_complete_tool_inventory(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    environment = {
        key: os.environ[key]
        for key in ("PATH", "HOME", "LANG", "LC_ALL")
        if key in os.environ
    }
    environment.update(
        {
            "PYTHONPATH": str(repository_root / "src"),
            "QA_ENVIRONMENT": "local",
            "QA_AUTH_MODE": "development",
            "QA_DATABASE_PATH": str(tmp_path / "mcp-runtime.sqlite3"),
            "DEFAULT_TEST_ENV": "qa",
            "QA_BASE_URL": "https://qa.example.test",
            "LLM_PROVIDER": "mock",
        }
    )
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "qa_mcp.server"],
        cwd=repository_root,
        env=environment,
    )

    async def discover() -> set[str]:
        with anyio.fail_after(30):
            async with stdio_client(parameters) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    return {tool.name for tool in response.tools}

    names = asyncio.run(discover())
    assert names == {
        "analyze_automation_failures", "analyze_requirement", "create_qa_project",
        "create_requirement_version", "create_suite_version", "execute_automation_code",
        "export_qa_project", "generate_automation", "generate_automation_code",
        "generate_automation_for_candidates", "generate_qa_suite", "generate_test_cases",
        "get_automation_execution", "get_automation_execution_report", "get_github_issue",
        "get_github_pull_request", "get_github_repository", "get_jira_issue", "get_qa_project",
        "get_requirement_version", "get_slack_channel", "get_slack_messages",
        "get_slack_thread", "get_suite_version", "health", "import_qa_project",
        "list_automation_executions", "list_requirement_versions", "list_suite_versions",
        "review_test_cases", "search_github_issues", "search_jira_issues",
        "search_slack_messages", "select_automation_candidates", "test_llm",
    }
