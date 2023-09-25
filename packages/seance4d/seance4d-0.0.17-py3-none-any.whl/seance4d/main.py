import sys
import threading
import wave
from array import array
from queue import Queue, Full

import pyaudio
import alsaaudio
import sounddevice as sd
from rich.pretty import pprint as print

try:
    from seance4d.open_ai import OpenAI
    from seance4d.text_parser import TextParser
    from seance4d.text_to_speech import TextToSpeech
except ImportError:
    from open_ai import OpenAI
    from text_parser import TextParser
    from text_to_speech import TextToSpeech


CHUNK_SIZE = 4096
MIN_VOLUME = 150
BUF_MAX_SIZE = CHUNK_SIZE * 100

CHANNELS = 1
INFORMAT = alsaaudio.PCM_FORMAT_FLOAT_LE
RATE = 44100
FRAMESIZE = 1024

# default text parser
text_parser = TextParser(prompt_text="hello alicia", end_text="spirit hear me")


def main():
    stopped: threading.Event = threading.Event()
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    listen_t = threading.Thread(target=listen, args=(stopped, q))
    listen_t.start()
    record_t = threading.Thread(target=record, args=(stopped, q))
    record_t.start()

    try:
        while True:
            listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

    listen_t.join()
    record_t.join()


def record(stopped: threading.Event, q):
    (
        current_fail_count,
        current_voice_count,
        filename,
        silence_count,
        wf,
    ) = set_variables()

    while True:
        if stopped.wait(timeout=0):
            break

        chunk = q.get()

        current_fail_count, current_voice_count = check_voice_volume(
            current_fail_count,
            current_voice_count,
            chunk,
            wf,
        )

        current_fail_count, current_voice_count, wf = check_success(
            current_fail_count,
            current_voice_count,
            filename,
            silence_count,
            stopped,
            wf,
        )


def check_success(
    current_fail_count,
    current_voice_count,
    filename,
    silence_count,
    stopped,
    wf,
):
    if current_fail_count > silence_count and current_voice_count > 1:
        wf.close()

        current_fail_count = 0
        current_voice_count = 0

        text_parser.parse(filename="output.wav")

        if text_parser.is_ready:
            ai_response = OpenAI().parse(text_parser.buffer)
            TextToSpeech().playback(
                stopped=stopped, reply=ai_response, text_parser=text_parser
            )

        # reset the wave file
        (
            current_fail_count,
            current_voice_count,
            filename,
            silence_count,
            wf,
        ) = set_variables()

        stopped.clear()

    return current_fail_count, current_voice_count, wf


def set_variables():
    current_fail_count = 0
    current_voice_count = 0
    silence_count = 50
    filename = "output.wav"
    wf = wave.open(filename, "wb")
    wf.setnchannels(2)
    wf.setframerate(44100)
    wf.setsampwidth(2)
    return current_fail_count, current_voice_count, filename, silence_count, wf


def check_voice_volume(
    CURRENT_FAIL_COUNT,
    CURRENT_VOICE_COUNT,
    chunk,
    wf,
):
    vol = max(chunk)

    if vol >= MIN_VOLUME:
        if CURRENT_VOICE_COUNT == 0:
            CURRENT_FAIL_COUNT = 0

        print("Sound detected")

        wf.writeframesraw(chunk)
        CURRENT_VOICE_COUNT += 1
    else:
        if CURRENT_VOICE_COUNT == 0:
            CURRENT_FAIL_COUNT = 0
        else:
            wf.writeframesraw(chunk)
            CURRENT_FAIL_COUNT += 1
    return CURRENT_FAIL_COUNT, CURRENT_VOICE_COUNT


def listen(stopped, q):
    print("Available devices:")
    print(alsaaudio.cards())

    try:
        indices = [
            (device_number, card_name)
            for device_number, card_name in enumerate(alsaaudio.cards())
            if "C930e" in card_name or "Dubler" in card_name
        ]

        print("Using device:")
        print(indices[0])

    except OSError:
        sys.exit(1)

    # set up audio input
    recorder = alsaaudio.PCM(
        type=alsaaudio.PCM_CAPTURE,
        channels=CHANNELS,
        rate=RATE,
        format=INFORMAT,
        periodsize=FRAMESIZE,
        device=f"hw:{indices[0][0]}",
    )

    while True:
        if stopped.wait(timeout=0):
            break
        try:
            q.put(array("h", recorder.read()[1]))
        except Full:
            pass  # discard


if __name__ == "__main__":
    main()
