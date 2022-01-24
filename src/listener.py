"""A keyboard listener to track user inputs."""

from src import config, utils
import time
import threading
import keyboard as kb
import os
from src.bot import Bot


class Listener:
    def __init__(self):
        """Initializes this Listener object's main thread."""

        self.thread = threading.Thread(target=Listener._main)
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
            if config.listening:
                if kb.is_pressed('f1'):
                    Bot.toggle_enabled()
                    time.sleep(0.667)
                elif kb.is_pressed('F2'):
                    config.calibrated = False
                    Bot.load_routine(config.routine)
                elif kb.is_pressed('f3'):
                    config.calibrated = False
                    Bot.load_routine()
                elif kb.is_pressed('F4'):
                    displayed_pos = tuple('{:.3f}'.format(round(i, 3)) for i in config.player_pos)
                    utils.print_separator()
                    print(f'Current position: ({displayed_pos[0]}, {displayed_pos[1]})')
                    with open('temp.txt', 'a') as f:
                        f.write(f'Current position: ({displayed_pos[0]}, {displayed_pos[1]})\n')
                    print("hp: ", config.player_status["hp"], " and mp: ", config.player_status["mp"])
                    time.sleep(0.5)
                elif kb.is_pressed('Esc'):
                    print("Closed by keyboard.")
                    os._exit(0)
            time.sleep(0.01)
