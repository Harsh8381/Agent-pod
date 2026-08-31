import speech_recognition as sr
import io


def transcribe_audio(audio_bytes):

    recognizer = sr.Recognizer()

    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)

    return recognizer.recognize_google(audio_data)