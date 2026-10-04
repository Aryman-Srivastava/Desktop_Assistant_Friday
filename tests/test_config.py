import json

import config


def test_load_contacts_normalizes_names(tmp_path, monkeypatch):
    contacts_path = tmp_path / "contacts.json"
    contacts_path.write_text(
        json.dumps({"Shiv": "shiv@example.com", "Arjun": "arjun@example.com"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(config, "CONTACTS_FILE", contacts_path)

    assert config.load_contacts() == {
        "shiv": "shiv@example.com",
        "arjun": "arjun@example.com",
    }
    assert config.resolve_contact_email("Shiv") == "shiv@example.com"
