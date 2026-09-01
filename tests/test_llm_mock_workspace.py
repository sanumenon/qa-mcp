from qa_mcp.core.llm import MockLLM


def test_mock_llm_returns_requirement_analysis_json():

    llm = MockLLM()

    response = llm.generate(
        """
        You are a senior QA engineer.

        Return ONLY valid JSON with exactly these fields:

        {
          "summary": "",
          "actors": []
        }
        """
    )

    assert response.startswith("{")
    assert '"summary"' in response
    assert '"actors"' in response


def test_mock_llm_returns_test_case_generation_json():

    llm = MockLLM()

    response = llm.generate(
        """
        Return ONLY valid JSON with exactly this structure:

        {
          "test_cases": []
        }
        """
    )

    assert response.startswith("{")
    assert '"test_cases"' in response
    assert '"TC001"' in response


def test_mock_llm_returns_review_json():

    llm = MockLLM()

    response = llm.generate(
        """
        Return ONLY valid JSON with exactly this structure:

        {
          "overall_quality": "Good",
          "coverage_score": 0
        }
        """
    )

    assert response.startswith("{")
    assert '"overall_quality"' in response
    assert '"coverage_score"' in response


def test_mock_llm_preserves_explicit_response():

    llm = MockLLM(
        response='{"custom": "response"}'
    )

    response = llm.generate(
        "Return JSON."
    )

    assert response == (
        '{"custom": "response"}'
    )

def test_mock_llm_routes_review_prompt_before_test_case_generation():

    llm = MockLLM()

    response = llm.generate(
        """
        Review the following generated test cases.

        Return ONLY valid JSON with exactly this structure:

        {
          "overall_quality": "Good",
          "coverage_score": 0,
          "test_cases": []
        }
        """
    )

    assert '"overall_quality"' in response
    assert '"coverage_score"' in response
    assert '"test_cases"' not in response