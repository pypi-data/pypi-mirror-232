import subprocess
from gtts import gTTS


class TextToSpeech:
    @staticmethod
    def playback(stopped, reply, text_parser):
        mytext = reply
        language = "en"

        myobj = gTTS(text=mytext, lang=language, slow=False)
        myobj.save("response.mp3")

        stopped.set()

        text_parser.reset()

        subprocess.call(
            ["mpg321", "response.mp3"],
            bufsize=4096,
            stdout=None,
            stderr=None,
        )
