from tools import web_search


def test_search_google_uses_supported_parameter_names(monkeypatch):
    seen = {}

    def fake_search(*args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return ["https://example.com"]

    monkeypatch.setattr(web_search, "search", fake_search)

    result = web_search.search_google("python", num_results=3)

    assert result == ["https://example.com"]
    assert seen["kwargs"]["sleep_interval"] == 2
    assert "pause" not in seen["kwargs"]
    assert seen["kwargs"]["timeout"] == 10
