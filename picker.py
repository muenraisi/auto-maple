import config
import time
import threading
from vkeys import press
from random import random

class Picker:
    def __init__(self):
        """Initializes this Listener object's main thread."""

        self.thread = threading.Thread(target=Picker._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\nStarted keyboard listener.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        while True:
            if config.pick_active:
                press("ctrl", 1, down_time=0.025, up_time=0.05)
                press("ctrl", 1, down_time=0.02, up_time=0.045)
                press("ctrl", 1, down_time=0.03, up_time=0.055)
            else:
                time.sleep(0.5)
