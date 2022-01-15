import time
import threading
from src.vkeys import press
from src import config


class Presser:
    def __init__(self):
        """Initializes this Pet object's main thread."""

        self.thread = threading.Thread(target=Presser._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts the Pet.
        :return:    None
        """

        print('\nStarted Presser.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly simulates the action of a pet.
        :return:    None
        """

        while True:
            if config.player_command:
                press(*config.player_command[0][0], *config.player_command[0][1])
                config.player_command = []
            else:
                time.sleep(0.05)

    @staticmethod
    def get_press_command(key, n, down_time=0.05, up_time=0.1):
        Presser._get_command([key, n], {"down_time": down_time, "up_time": up_time})

    @staticmethod
    def _get_command(args, kwargs):
        while True:
            if config.player_command:
                time.sleep(0.01)
            else:
                config.player_command = [(args, kwargs)]
