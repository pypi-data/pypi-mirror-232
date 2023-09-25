from dataclasses import dataclass
import time
import ctypes
from termcolor import colored


def countdown(text, mins):
    t = mins
    while t:
        timer = ' - {:02d} mins left'.format(t)
        print('\r' + text + colored(timer, 'green'), end='')
        #TODO: REVERT BELOW!!!
        time.sleep(1)
        t -= 1

    ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)

    input(f"\r{text} - Time up, carry on?")


@dataclass
class SpecialPrompt:
    text: str
    durationMins: int

    def show(self):
        countdown(self.text, self.durationMins)


SPECIAL_PROMPTS = [
    SpecialPrompt('Strategy Time', 15),
    SpecialPrompt('Mail and slack', 2)
]
