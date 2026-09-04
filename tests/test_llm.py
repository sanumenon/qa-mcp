import pytest

from qa_mcp.core.llm import MockLLM, create_llm


def test_mock_llm_generates_response():
    llm = MockLLM(response="hello")

    assert llm.generate("test prompt") == "hello"


def test_mock_llm_rejects_empty_prompt():
    llm = MockLLM()

    with pytest.raises(ValueError):
        llm.generate("")


def test_create_llm_uses_mock_provider():
    config = {
        "llm": {
            "provider": "mock"
        }
    }

    llm = create_llm(config)

    assert isinstance(llm, MockLLM)


def test_create_llm_rejects_unknown_provider():
    config = {
        "llm": {
            "provider": "unknown"
        }
    }

    with pytest.raises(ValueError):
        create_llm(config)

def test_bedrock_llm_extracts_kimi_response():
    from qa_mcp.core.llm import BedrockLLM

    class FakeClient:
        def converse(self, **kwargs):
            assert kwargs["modelId"] == "moonshotai.kimi-k2.5"
            assert kwargs["messages"][0]["content"][0]["text"] == "hello"

            return {
                "output": {
                    "message": {
                        "content": [
                            {"text": " OK"}
                        ]
                    }
                }
            }

    llm = object.__new__(BedrockLLM)
    llm.model_id = "moonshotai.kimi-k2.5"
    llm.client = FakeClient()

    assert llm.generate("hello") == " OK"


def test_bedrock_llm_extracts_anthropic_response():
    from qa_mcp.core.llm import BedrockLLM

    class FakeClient:
        def converse(self, **kwargs):
            assert kwargs["modelId"] == (
                "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
            )
            assert kwargs["messages"][0]["content"][0]["text"] == "hello"

            return {
                "output": {
                    "message": {
                        "content": [
                            {"text": "hello"}
                        ]
                    }
                }
            }

    llm = object.__new__(BedrockLLM)
    llm.model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    llm.client = FakeClient()

    assert llm.generate("hello") == "hello"


def test_bedrock_llm_rejects_empty_prompt():
    from qa_mcp.core.llm import BedrockLLM

    llm = object.__new__(BedrockLLM)
    llm.model_id = "moonshotai.kimi-k2.5"

    with pytest.raises(ValueError):
        llm.generate("")


def test_bedrock_llm_requires_region():
    from qa_mcp.core.llm import BedrockLLM

    with pytest.raises(ValueError):
        BedrockLLM(
            region="",
            model_id="moonshotai.kimi-k2.5",
        )


def test_bedrock_llm_requires_model_id():
    from qa_mcp.core.llm import BedrockLLM

    with pytest.raises(ValueError):
        BedrockLLM(
            region="us-east-1",
            model_id="",
        )
