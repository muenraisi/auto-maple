import threading
import numpy as np
from collections import deque
import mss

import config
import utils


class Camera:
    def __init__(self):
        """Initializes this Listener object's main thread."""

        self.thread = threading.Thread(target=Camera._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\nStarted Camera.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """
        config.frames = deque(maxlen=10)
        with mss.mss() as sct:
            while True:
                frame = np.array(sct.grab(config.MONITOR))
                if not config.cropped:
                    # crop the monitor to the game windows
                    tl, br = utils.single_match(frame[:frame.shape[0] // 8,
                                                :],
                                                config.HEADER_TEMPLATE)
                    config.MONITOR = {'top': br[1], 'left': tl[0], 'width': 1366, 'height': 768}
                    config.cropped = True
                else:
                    config.frames.append(frame)
