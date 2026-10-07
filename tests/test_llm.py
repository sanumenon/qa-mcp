import pytest

from qa_mcp.core.llm import (
    BedrockLLM,
    LLMGenerationError,
    MockLLM,
    create_llm,
)

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

def test_bedrock_llm_rejects_guardrail_intervention():
    class FakeClient:
        def converse(self, **kwargs):
            return {
                "stopReason": "guardrail_intervened",
                "output": {
                    "message": {
                        "content": []
                    }
                }
            }

    llm = object.__new__(BedrockLLM)
    llm.model_id = "moonshotai.kimi-k2.5"
    llm.client = FakeClient()

    with pytest.raises(
        LLMGenerationError,
        match="Bedrock guardrails blocked LLM generation",
    ):
        llm.generate("hello")


def test_bedrock_llm_rejects_empty_response_content():
    class FakeClient:
        def converse(self, **kwargs):
            return {
                "stopReason": "end_turn",
                "output": {
                    "message": {
                        "content": []
                    }
                }
            }

    llm = object.__new__(BedrockLLM)
    llm.model_id = "moonshotai.kimi-k2.5"
    llm.client = FakeClient()

    with pytest.raises(
        LLMGenerationError,
        match="Bedrock returned an empty LLM response",
    ):
        llm.generate("hello")


def test_bedrock_llm_uses_configured_http_settings(monkeypatch):
    from qa_mcp.core.llm import BedrockLLM

    captured = {}

    class FakeConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            captured["config_kwargs"] = kwargs

    class FakeBoto3:
        @staticmethod
        def client(service_name, region_name, config):
            captured["service_name"] = service_name
            captured["region_name"] = region_name
            captured["config"] = config
            return object()

    import sys
    import types

    fake_boto3 = types.SimpleNamespace(
        client=FakeBoto3.client
    )

    fake_botocore_config = types.SimpleNamespace(
        Config=FakeConfig
    )

    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)
    monkeypatch.setitem(
        sys.modules,
        "botocore.config",
        fake_botocore_config,
    )

    BedrockLLM(
        region="us-east-1",
        model_id="test-model",
        connect_timeout_seconds=45,
        read_timeout_seconds=180,
        retry_mode="standard",
        max_attempts=1,
    )

    assert captured["service_name"] == "bedrock-runtime"
    assert captured["region_name"] == "us-east-1"
    assert captured["config"].kwargs["connect_timeout"] == 45
    assert captured["config"].kwargs["read_timeout"] == 180
    assert captured["config"].kwargs["retries"] == {
        "mode": "standard",
        "max_attempts": 1,
    }


def test_bedrock_llm_rejects_invalid_timeout():
    from qa_mcp.core.llm import BedrockLLM

    with pytest.raises(
        ValueError,
        match="Bedrock connect timeout must be greater than zero",
    ):
        BedrockLLM(
            region="us-east-1",
            model_id="test-model",
            connect_timeout_seconds=0,
        )

    with pytest.raises(
        ValueError,
        match="Bedrock read timeout must be greater than zero",
    ):
        BedrockLLM(
            region="us-east-1",
            model_id="test-model",
            read_timeout_seconds=0,
        )


def test_bedrock_llm_rejects_invalid_max_attempts():
    from qa_mcp.core.llm import BedrockLLM

    with pytest.raises(
        ValueError,
        match="Bedrock max attempts must be greater than zero",
    ):
        BedrockLLM(
            region="us-east-1",
            model_id="test-model",
            max_attempts=0,
        )


def test_load_config_reads_bedrock_settings(monkeypatch):
    from qa_mcp.core.config import load_config

    monkeypatch.setenv(
        "BEDROCK_CONNECT_TIMEOUT_SECONDS",
        "45",
    )
    monkeypatch.setenv(
        "BEDROCK_READ_TIMEOUT_SECONDS",
        "180",
    )
    monkeypatch.setenv(
        "BEDROCK_RETRY_MODE",
        "standard",
    )
    monkeypatch.setenv(
        "BEDROCK_MAX_ATTEMPTS",
        "1",
    )

    config = load_config()

    assert config["llm"]["connect_timeout_seconds"] == 45
    assert config["llm"]["read_timeout_seconds"] == 180
    assert config["llm"]["retry_mode"] == "standard"
    assert config["llm"]["max_attempts"] == 1
