import subprocess
import threading

from gtts import gTTS


class TextToSpeech:
    @staticmethod
    def playback(stopped: threading.Event, reply, text_parser):
        mytext = reply
        language = "en"

        # use Google Text to Speech
        gTTS(text=mytext, lang=language, slow=False).save("response.mp3")

        if stopped is not None:
            stopped.set()

        if text_parser is not None:
            text_parser.reset()

        subprocess.call(
            ["mpg321", "response.mp3"],
            bufsize=4096,
            stdout=None,
            stderr=None,
        )

        if stopped is not None:
            stopped.clear()
