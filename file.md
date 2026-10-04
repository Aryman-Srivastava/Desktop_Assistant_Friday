# Friday Desktop Assistant - Upgrade Requirements & Task List

This document outlines the prioritized tasks for upgrading the Friday Desktop Assistant from a script-based automation tool to a secure, robust, and evaluated AI engineering project.

## Phase 1: Security & Configuration Hygiene (Critical)
- [x] **Remove Insecure Serialization:** Delete `pickle` usage and `login.txt`. 
- [x] **Secrets Management:** Implement `.env` (via `python-dotenv`) or a secure `credentials.json` to store secrets.
- [x] **Secure Authentication:** Transition Gmail SMTP to use App Passwords or OAuth2. Never store plaintext passwords.
- [x] **Externalize Contacts:** Remove hardcoded email addresses (Varun, Shiv, Arjun) and store them in a `contacts.json` file.
- [x] **Remove Hardcoded Paths:** Move absolute paths (Chrome executable, PyCharm executable) to a configuration file or environment variables.

## Phase 2: Project Packaging & Environment
- [x] **Dependency Management:** Create a `requirements.txt` or `pyproject.toml` to track dependencies (`SpeechRecognition`, `pyttsx3`, `wikipedia`, etc.).
- [x] **Git Configuration:** Add a standard Python `.gitignore` file.
- [x] **Environment Template:** Create `resources/.env.example` documenting required variables without exposing real keys.
- [x] **Documentation:** Update `README.md` with architecture diagrams, installation steps, and usage examples.

## Phase 3: Architectural Refactoring
- [x] **Modularize Codebase:** Break the monolithic `Main.py` into distinct modules:
  - `config/` (configuration and secrets loading)
  - `assistant/` (TTS and STT handling, command dispatch, and tool actions)
  - `router.py` (command parsing and execution)
  - `skills/` or `integrations/` (separate files for Email, Web Search, System OS tasks)
- [ ] **Command Registry:** Replace the extensive `if/elif` string-matching chain with a structured Command Registry or Dispatcher pattern.

## Phase 4: AI & NLP Integration
- [x] **Whisper Speech Recognition:** Replace the PyAudio/Google Speech Recognition path with local `faster-whisper` transcription using `sounddevice`.
- [ ] **Intent Classification:** Replace brittle substring checks (e.g., `"youtube" in query`) with structured intent recognition.
- [ ] **LLM Integration:** Implement a lightweight local LLM (e.g., Ollama) or hosted API (OpenAI/Anthropic) to map user utterances to specific functional schemas.
- [ ] **Structured Outputs:** Use `Pydantic` models to define expected arguments for each command (e.g., extracting the recipient name and message content from an email request).
- [ ] **Context & Memory:** Add short-term conversational memory for multi-step flows (e.g., remembering the email recipient while asking for the message body).

## Phase 5: Reliability, Error Handling & Safety
- [ ] **Specific Exception Handling:** Remove bare `except Exception as e:` blocks. Catch specific errors (e.g., `smtplib.SMTPException`, `requests.exceptions.Timeout`).
- [ ] **Network Timeouts:** Add explicit timeouts to all network requests (Wikipedia, YouTube search, SMTP).
- [ ] **Action Confirmation:** Require explicit user confirmation ("Are you sure you want to send this email?") before executing sensitive external actions.
- [ ] **Structured Logging:** Implement Python's native `logging` module to log warnings, errors, and system states to a file instead of relying on `print()`.

## Phase 6: Testing & Evaluation
- [ ] **Unit Testing:** Write `pytest` test cases for command routing, configuration loading, and contact resolution.
- [ ] **Mocking:** Use `unittest.mock` to test email and web search logic without hitting external APIs.
- [ ] **Evaluation Dataset:** Create a JSON dataset of sample utterances mapped to expected intents.
- [ ] **Performance Metrics:** Measure and report on intent classification accuracy, speech recognition failure rate, and overall request latency.