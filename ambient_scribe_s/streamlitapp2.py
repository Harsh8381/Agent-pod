import requests

BASE_URL = "http://127.0.0.1:8000"


def generate_note(
    patient_name,
    patient_age,
    patient_gender,
    doctor_name,
    transcript
):
    response = requests.post(
        f"{BASE_URL}/api/summary/generate-note",
        json={
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "doctor_name": doctor_name,
            "transcript": transcript
        }
    )

    response.raise_for_status()

    return response.json()


def detect_insights(transcript):

    response = requests.post(
        f"{BASE_URL}/api/summary/insights",
        json={
            "transcript": transcript
        }
    )

    response.raise_for_status()

    return response.json()


def transcribe_audio(audio_bytes):

    files = {
        "file": (
            "audio.wav",
            audio_bytes,
            "audio/wav"
        )
    }

    response = requests.post(
        f"{BASE_URL}/api/transcription/upload",
        files=files
    )

    response.raise_for_status()

    return response.json()


def get_records():

    response = requests.get(
        f"{BASE_URL}/api/records"
    )

    response.raise_for_status()

    return response.json()


def get_record(record_id):

    response = requests.get(
        f"{BASE_URL}/api/records/{record_id}"
    )

    response.raise_for_status()

    return response.json()


def save_record(
    name,
    age,
    gender,
    doctor,
    transcript,
    summary
):

    response = requests.post(
        f"{BASE_URL}/api/records",
        json={
            "name": name,
            "age": age,
            "gender": gender,
            "doctor": doctor,
            "transcript": transcript,
            "summary": summary
        }
    )

    response.raise_for_status()

    return response.json()


def update_record(
    record_id,
    summary
):

    response = requests.put(
        f"{BASE_URL}/api/records/{record_id}",
        json={
            "summary": summary
        }
    )

    response.raise_for_status()

    return response.json()


def approve_record(record_id):

    response = requests.put(
        f"{BASE_URL}/api/records/{record_id}/approve"
    )

    response.raise_for_status()

    return response.json()