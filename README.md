# Friday Desktop Assistant

Friday is a Windows voice assistant for web navigation, Wikipedia lookups, YouTube playback, local file opening, and email through Gmail SMTP.

The project has been updated to follow a more AI-engineering-friendly structure by separating configuration, command routing, and intent parsing from the main runtime loop.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

	```powershell
	python -m pip install -r requirements.txt
	```

3. Copy `resources/.env.example` to `resources/.env` and set `FRIDAY_GMAIL_ADDRESS` and `FRIDAY_GMAIL_APP_PASSWORD`.
4. Use a Gmail App Password, not the normal Gmail account password. Keep `resources/.env` private.
5. Adjust `FRIDAY_BROWSER_EXECUTABLE` and `FRIDAY_PYCHARM_EXECUTABLE` if those applications are installed outside their usual locations.
6. Start Friday:

	```powershell
	python Main.py
	```

## Architecture

```text
Main.py
  |-- config/
  |    |-- __init__.py       configuration loading and contact resolution
  |-- assistant/
  |    |-- intent_parser.py  lightweight multilingual intent detection
  |    |-- router.py         typed command registry / dispatcher
  |-- resources/
  |    |-- .env              local secrets (ignored by git)
  |    |-- .env.example
  |    |-- contacts.json     name-to-email mapping
```

The assistant now follows a command-dispatch model instead of a single long `if/elif` block. Intent parsing is structured, configurable, and easier to replace with an LLM or local model later.

## AI-engineering improvements included

- Secret management through `.env`
- Contact resolution from `contacts.json`
- Safe email confirmation before sending
- Centralized command routing
- Structured intent parsing for common commands
- Logging for runtime issues and command failures
- Unit tests covering configuration loading and intent detection

## Example commands

- "What time is it?"
- "Search for Python tutorials"
- "Play deep learning music on YouTube"
- "Email Shiv with project update"
- "Exit"
