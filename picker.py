import config
import time
import threading
from vkeys import press
import utils
from random import random


class Picker:
    def __init__(self):
        """Initializes this Picker object's main thread."""

        self.thread = threading.Thread(target=Picker._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts the Picker.
        :return:    None
        """

        print('\nStarted Pet.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly simulates the action of a pet.
        :return:    None
        """

        while True:
            if config.enabled:
                Picker._pickup()
            else:
                time.sleep(0.01)

    @staticmethod
    @utils.run_if_enabled
    def _pickup():
        press("ctrl", 1, down_time=0.025, up_time=0.05)
        press("ctrl", 1, down_time=0.02, up_time=0.045)
        press("ctrl", 1, down_time=0.03, up_time=0.055)
