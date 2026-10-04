from assistant.intent_parser import parse_user_intent


def test_email_intent_parses_known_contact():
    result = parse_user_intent("email shiv hello there", {"shiv": "shiv@example.com"})

    assert result.intent == "send_email"
    assert result.requires_confirmation is True
    assert result.parameters["recipient"] == "shiv"
    assert "hello there" in result.parameters["message"]


def test_search_intent_returns_search_query():
    result = parse_user_intent("search for python tutorials")

    assert result.intent == "search_web"
    assert "python tutorials" in result.parameters["query"]


def test_unknown_intent_is_handled_gracefully():
    result = parse_user_intent("hello friday can you do something random")

    assert result.intent == "unknown"
