from tools.registry import TOOL_REGISTRY


def test_tool_registry_contains_core_capabilities():
    expected = {"web_search", "open_url", "wikipedia", "play_media", "time", "open_python", "find_file", "send_email"}
    assert set(TOOL_REGISTRY) == expected
    assert TOOL_REGISTRY["web_search"].name == "web_search"
