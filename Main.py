"""Windows voice assistant entry point."""

from __future__ import annotations

import datetime
import json
import logging
import os
import random
import smtplib
import sys
from typing import Any, cast

import numpy as np
import pyttsx3
import sounddevice as sd
import webbrowser
import wikipedia
from faster_whisper import WhisperModel
from googlesearch import search
from youtube_search import YoutubeSearch

from assistant.intent_parser import parse_user_intent
from assistant.router import CommandRouter
from config import (
    BROWSER_EXECUTABLE,
    PYCHARM_EXECUTABLE,
    load_contacts,
    require_email_credentials,
    resolve_contact_email,
)

engine = pyttsx3.init("sapi5")
voices = cast(list[Any], engine.getProperty("voices") or [])
if not voices:
    raise RuntimeError("No speech voices were detected from pyttsx3.")
voice = voices[1] if len(voices) > 1 else voices[0]
engine.setProperty("voice", voice.id)

logging.basicConfig(
    filename="friday.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")


def search_google(query2: str, num_results: int = 5) -> list[str]:
    """Query Google and return the first few result URLs."""
    links2 = []
    for j in search(term=query2, num_results=num_results, sleep_interval=2, timeout=10):
        links2.append(j)
    return links2


def speak(audio: str) -> None:
    engine.say(audio)
    engine.runAndWait()


def takeCommand() -> str | None:
    """Record a few seconds of audio and transcribe it with local Whisper."""
    sample_rate = 16000
    duration_seconds = 5

    try:
        print("Listening...")
        audio_data = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        print("Recognizing with Whisper...")
        audio_data = np.squeeze(audio_data)
        segments, _ = whisper_model.transcribe(audio_data, beam_size=5)
        query = "".join(segment.text for segment in segments).strip()
        print(f"USER SAID: {query}\n")
        return query or None
    except (sd.PortAudioError, RuntimeError, ValueError) as error:
        logging.warning("Whisper audio capture failed: %s", error)
        speak("SAY THAT AGAIN PLEASE...")
        return None


def sendEmail(to2: str, content2: str) -> bool:
    """Send an email using the configured Gmail app password."""
    sender, password = require_email_credentials()
    normalized_name = to2.strip().lower()
    recipient = resolve_contact_email(normalized_name)

    if recipient is None and " " in normalized_name:
        recipient = resolve_contact_email(normalized_name.split()[-1])

    if recipient is None:
        speak("not in list")
        return False

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, content2)
    return True


def open_url(url: str) -> None:
    """Open a URL with the configured browser or the system default."""
    try:
        if BROWSER_EXECUTABLE:
            browser = webbrowser.BackgroundBrowser(BROWSER_EXECUTABLE)
            browser.open(url)
            return
        webbrowser.open(url)
    except (OSError, webbrowser.Error):
        webbrowser.open(url)


def greetings(string: str) -> str:
    statements = ["Hello, Mr. Aryman", "Hi, Mr. Aryman"]
    statements.append(string)
    audio = random.choice(statements)
    statements.pop()
    return audio


def wishMe() -> None:
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak(greetings("Good Morning, Mr. Aryman"))
    elif 12 <= hour < 15:
        speak(greetings("Good Afternoon, Mr. Aryman"))
    else:
        speak(greetings("Good Evening, Mr. Aryman"))
    speak("I AM FRIDAY, HOW CAN I BE OF HELP TO YOU SIR")


def confirm_action(prompt: str) -> bool:
    """Require explicit confirmation for destructive or external actions."""
    speak(prompt)
    response = takeCommand()
    if response is None:
        return False
    return any(keyword in response.lower() for keyword in ("yes", "sure", "confirm", "proceed"))


def handle_wikipedia(params: dict[str, str], context: dict[str, Any]) -> bool:
    topic = (params.get("topic") or "").strip()
    if not topic:
        speak("What would you like me to look up?")
        return False

    speak("Searching Wikipedia...")
    try:
        result = wikipedia.summary(topic, sentences=2)
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ValueError):
        try:
            result = wikipedia.summary(topic.replace(" ", ""), sentences=2)
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ValueError):
            speak("I could not find a matching Wikipedia page")
            return False
    speak("According to wikipedia")
    speak(result)
    return True


def handle_play_media(params: dict[str, str], context: dict[str, Any]) -> bool:
    query = (params.get("query") or "").strip()
    if not query:
        speak("What should I play?")
        return False

    speak("opening")
    results = YoutubeSearch(query, max_results=10).to_json()
    results = json.loads(results)
    videos = results.get("videos") or []
    if not videos:
        speak("I could not find a matching YouTube result")
        return False

    url = "https://www.youtube.com/" + videos[0]["url_suffix"]
    open_url(url)
    return True


def handle_search_web(params: dict[str, str], context: dict[str, Any]) -> bool:
    query = (params.get("query") or "").strip()
    if not query:
        speak("What would you like me to search for?")
        return False

    links = search_google(query)
    if not links:
        speak("No results found")
        return False

    open_url(str(links[0]))
    return True


def handle_time(params: dict[str, str], context: dict[str, Any]) -> bool:
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"the time is {strTime}")
    return True


def handle_open_python(params: dict[str, str], context: dict[str, Any]) -> bool:
    if PYCHARM_EXECUTABLE and os.path.exists(PYCHARM_EXECUTABLE):
        os.startfile(PYCHARM_EXECUTABLE)
        return True
    speak("PyCharm path is not configured")
    return False


def handle_send_email(params: dict[str, str], context: dict[str, Any]) -> bool:
    recipient = (params.get("recipient") or "").strip()
    content = (params.get("message") or "").strip()

    if not recipient:
        speak("to whom should i send the message?")
        recipient = takeCommand() or ""
    if not content:
        speak("what should i say")
        content = takeCommand() or ""
    if not recipient or not content:
        speak("I need both a message and a recipient")
        return False

    if not confirm_action("Are you sure you want to send this email?"):
        speak("email cancelled")
        return False

    if sendEmail(recipient, content):
        speak("email sent")
        return True
    return False


def handle_find_file(params: dict[str, str], context: dict[str, Any]) -> bool:
    filename = (params.get("query") or "").strip()
    if not filename:
        speak("What file should I look for?")
        return False

    result = []
    for root, _, files in os.walk("C:"):
        if filename.lower() in [item.lower() for item in files]:
            result.append(os.path.join(root, filename))

    if result:
        os.startfile(result[0])
        return True

    speak("file not found")
    return False


def handle_exit(params: dict[str, str], context: dict[str, Any]) -> bool:
    speak("have a great day sir")
    sys.exit()


command_router = CommandRouter()
command_router.register("wikipedia", handle_wikipedia)
command_router.register("play_media", handle_play_media)
command_router.register("search_web", handle_search_web)
command_router.register("time", handle_time)
command_router.register("open_python", handle_open_python)
command_router.register("send_email", handle_send_email)
command_router.register("find_file", handle_find_file)
command_router.register("exit", handle_exit)


if __name__ == "__main__":
    wishMe()
    while True:
        raw_query = takeCommand()
        if not raw_query:
            continue

        cleaned_query = raw_query.strip()
        if not cleaned_query:
            continue

        intent = parse_user_intent(cleaned_query, load_contacts())
        if intent.intent == "unknown":
            logging.info("Unhandled voice input: %s", cleaned_query)
            speak("I could not understand that command")
            continue

        if intent.requires_confirmation and not confirm_action("Would you like me to proceed?"):
            speak("Action cancelled")
            continue

        try:
            from assistant.actions import run_action
            from assistant.guardrails import validate_intent

            validation = validate_intent(intent)
            if not validation.ok:
                speak(validation.message)
                continue

            result = run_action(intent)
            if result.message:
                speak(result.message)
        except (SystemExit, KeyError, OSError, RuntimeError, ValueError, smtplib.SMTPException) as error:
            logging.exception("Command execution failed: %s", error)
            speak("I could not complete that request")
