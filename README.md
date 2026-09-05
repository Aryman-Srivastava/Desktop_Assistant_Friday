# Friday Desktop Assistant

Friday is a Windows voice assistant for web navigation, Wikipedia lookups, YouTube playback, local file opening, and email through Gmail SMTP.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

	```powershell
	python -m pip install -r requirements.txt
	```

3. Copy `.env.example` to `.env` and set `FRIDAY_GMAIL_ADDRESS` and `FRIDAY_GMAIL_APP_PASSWORD`.
4. Use a Gmail App Password, not the normal Gmail account password. Keep `.env` private.
5. Adjust `FRIDAY_BROWSER_EXECUTABLE` and `FRIDAY_PYCHARM_EXECUTABLE` if those applications are installed outside their usual locations.
6. Start Friday:

	```powershell
	python fridayMain.py
	```

## Architecture

```text
fridayMain.py
  |-- config.py       environment variables and contacts.json
	|-- audio           sounddevice recording, faster-whisper STT, and pyttsx3 TTS
  |-- integrations    Gmail, Wikipedia, Google, YouTube, and Windows actions
```

Contacts are maintained in `contacts.json` as a name-to-email mapping. The remaining command loop is intentionally kept in `fridayMain.py` while the later modularization tasks are completed.
