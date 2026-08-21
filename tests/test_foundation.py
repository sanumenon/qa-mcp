from qa_mcp.core.config import load_config


def test_config_loads():
    config = load_config()

    assert config["application"]["name"] == "qa-mcp"
    assert config["features"]["testcase_generator"] is True
