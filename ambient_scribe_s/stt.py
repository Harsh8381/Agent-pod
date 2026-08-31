import sounddevice as sd
import soundfile as sf

DURATION = 5
SAMPLE_RATE = 16000

print("Speak now...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write("audio.wav", audio, SAMPLE_RATE)

print("Saved audio.wav")