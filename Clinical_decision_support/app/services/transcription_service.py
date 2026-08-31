import io

import speech_recognition as sr


class TranscriptionService:
    def transcribe(self, audio_bytes: bytes) -> str:
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)