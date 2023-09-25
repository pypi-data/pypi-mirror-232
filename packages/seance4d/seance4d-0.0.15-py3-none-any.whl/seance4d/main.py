import sys
import threading
import wave
from array import array
from queue import Queue, Full

import pyaudio
import sounddevice as sd
from rich.pretty import pprint as print
from seance4d.open_ai import OpenAI
from seance4d.text_parser import TextParser
from seance4d.text_to_speech import TextToSpeech

# from open_ai import OpenAI
# from text_parser import TextParser
# from text_to_speech import TextToSpeech

CHUNK_SIZE = 4096
MIN_VOLUME = 500
BUF_MAX_SIZE = CHUNK_SIZE * 100

# default text parser
text_parser = TextParser(prompt_text="hello alicia", end_text="spirit hear me")


def main():
    stopped = threading.Event()
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


def record(stopped, q):
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
        set_variables()

        main()
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
    try:
        indices = [
            s for i, s in enumerate(sd.query_devices()) if "Dubler" in s["name"]
        ]

        print("Using device:")
        print(indices)

        stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=int(indices[0]["default_samplerate"]),
            input=True,
            frames_per_buffer=1024,
            input_device_index=indices[0]["index"],
        )
    except OSError:
        sys.exit(1)

    while True:
        if stopped.wait(timeout=0):
            break
        try:
            data = array("h")
            data.fromstring(stream.read(CHUNK_SIZE))
            q.put(data)
            # q.put(array("h", stream.read(CHUNK_SIZE)))
        except Full:
            pass  # discard


if __name__ == "__main__":
    main()
