"""Windows voice assistant entry point."""

import datetime
import json
import logging
import os
import random
import sys
import numpy as np
import sounddevice as sd
from youtube_search import YoutubeSearch
from faster_whisper import WhisperModel
import pyttsx3
import wikipedia
import webbrowser
import smtplib
from googlesearch import search
from config import (
    BROWSER_EXECUTABLE,
    PYCHARM_EXECUTABLE,
    load_contacts,
    require_email_credentials,
)

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

logging.basicConfig(
    filename="friday.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")


def search_google(query2):
    links2 = []
    for j in search(term=query2, num_results=5):
        links2.append(j)
    return links2


def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    """Record five seconds of audio and transcribe it with local Whisper."""
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
        return query
    except (sd.PortAudioError, RuntimeError) as error:
        logging.warning("Whisper audio capture failed: %s", error)
        speak("SAY THAT AGAIN PLEASE...")
        return None


def sendEmail(to2, content2):
    sender, password = require_email_credentials()
    recipient_name = to2.split()[-1].lower()
    recipient = load_contacts().get(recipient_name)
    if recipient is None:
        speak("not in list")
        return False

    with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, content2)
    return True


def open_url(url):
    """Open a URL with the configured browser or the system default."""
    if BROWSER_EXECUTABLE:
        browser = webbrowser.BackgroundBrowser(BROWSER_EXECUTABLE)
        browser.open(url)
    else:
        webbrowser.open(url)

def greetings(string):
    statements = ["Hello, Mr. Aryman", "Hi, Mr. Aryman"]
    statements.append(string)
    audio = random.choice(statements)
    statements.pop()
    return audio

def wishMe():

    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        audio = greetings("Good Morning, Mr. Aryman")
        speak(audio)
    elif 12 <= hour < 15:
        audio = greetings("Good Afternoon, Mr. Aryman")
        speak(audio)
    else:
        audio = greetings("Good Evening, Mr. Aryman")
        speak(audio)
    speak("I AM FRIDAY, HOW CAN I BE OF HELP TO YOU SIR")
    return None

if __name__ == '__main__':
    wishMe()
    while True:
        query = takeCommand()
        if query:
            query = query.lower()
        else:
            continue

        # WIKIPEDIA SEARCH
        if "wikipedia" in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                result = wikipedia.summary(query, sentences=2)
            except Exception as e:
                query = query.replace(" ", "")
                result = wikipedia.summary(query, sentences=2)
            speak("According to wikipedia")
            # print(result)
            speak(result)

        # OPEN YOUTUBE
        elif "youtube" in query:
            open_url("https://youtube.com")

        # OPEN GOOGLE
        elif "google" in query:
            open_url("https://google.com")

        # OPEN STACKOVERFLOW
        elif "stackoverflow" in query:
            open_url("https://stackoverflow.com")

        # PLAY MUSIC USING YOUTUBE
        elif "play" in query:
            # music_dir = URL HERE
            # songs = os.listdir(music_dir)
            # os.startfile(os.path.join(music_dir, songs[0]))
            speak("opening")
            query = query.replace("play", "")
            results = YoutubeSearch(query, max_results=10).to_json()
            results = json.loads(results)
            url_suffix = results["videos"][0]["url_suffix"]
            url = "https://www.youtube.com/" + url_suffix
            open_url(url)

        # TELL TIME
        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"the time is {strTime}")

        # OPEN PYCHARM
        elif "python" in query:
            if PYCHARM_EXECUTABLE and os.path.exists(PYCHARM_EXECUTABLE):
                os.startfile(PYCHARM_EXECUTABLE)
            else:
                speak("PyCharm path is not configured")

        # SEND EMAIL
        elif "email" in query:
            try:
                speak("what should i say")
                content = takeCommand()
                speak("to whom should i send the message?")
                to = takeCommand()
                if not content or not to:
                    speak("I need both a message and a recipient")
                    continue
                if sendEmail(to, content):
                    speak("email sent")
            except (RuntimeError, OSError, smtplib.SMTPException, ValueError) as error:
                logging.exception("Email failed: %s", error)
                speak("sorry the process has been failed")

        # SEARCH GOOGLE
        elif 'search' in query:
            if query == "search":
                continue
            query = query.replace("search", "")
            links = search_google(query)
            if links:
                open_url(str(links[0]))

        # FINDING FILE IN OS
        elif 'os' in query.lower():
            query = query.replace("os ", "")
            query = query.replace("OS ", "")
            query = query.replace("Os ", "")
            query = query.replace("oS ", "")
            result = []
            for root, _, files in os.walk("C:"):
                if query.lower() in files:
                    result.append(os.path.join(root, query))
            if result:
                os.startfile(result[0])
            else:
                speak("file not found")

        # EXIT
        elif "exit" in query:
            speak("have a great day sir")
            sys.exit()
