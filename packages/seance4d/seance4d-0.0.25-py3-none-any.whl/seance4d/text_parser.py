import os

import speech_recognition as sr
from rich.pretty import pprint as print


class TextParser:
    def __init__(
        self,
        prompt_text="hello alicia",
        end_text="spirit hear me",
        end_program_text="end program",
        shutdown_text="stop it now",
    ):
        self.prompt_text = prompt_text
        self.shutdown_text = shutdown_text
        self.end_text = end_text
        self.end_program_text = end_program_text
        self.found_prompt = False
        self.is_ready = False
        self.buffer = ""

    def reset(self):
        self.__init__(prompt_text=self.prompt_text, end_text=self.end_text)

    def parse(self, filename="output.wav"):
        r = sr.Recognizer()

        with sr.AudioFile(filename) as source:
            # convert from speech to text
            try:
                text = r.recognize_google(r.record(source))

                if self.end_program_text.lower() in text.lower():
                    print(f"End program command received")
                    self.buffer = ""
                    self.is_ready = False
                    os._exit(0)

                if self.shutdown_text.lower() in text.lower():
                    print(f"Shutdown command received")
                    self.buffer = ""
                    self.is_ready = False
                    os.system("shutdown /s /t 1")

                if (
                    not self.found_prompt
                    and self.prompt_text.lower() in text.lower()
                ):
                    # if we haven't found the prompt yet, and we find it
                    print(f"Starting with {text}")

                    self.found_prompt = True
                    self.buffer = text.lower().split(self.prompt_text.lower())[
                        1
                    ]
                elif (
                    self.found_prompt and self.end_text.lower() in text.lower()
                ):
                    # if we have found the prompt, and we find the end text
                    print(f"Ending with {text}")
                    self.buffer += text.lower().split(self.end_text.lower())[0]
                    self.is_ready = True
                elif self.found_prompt:
                    # if we have found the prompt, and we haven't found the
                    # end text
                    print(f"Appending {text}")
                    self.buffer += text
                else:
                    # if we haven't found the prompt yet, and we haven't found
                    # the end text
                    print(f"Audio discarded: {text}")
            except sr.UnknownValueError:
                print(f"Ditching indecipherable text")
            except sr.RequestError as e:
                print(
                    f"Could not request results from Google Speech "
                    f"Recognition service; {e}"
                )
