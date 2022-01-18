import threading
import numpy as np
from collections import deque
import mss
import time
import cv2

from src import config, utils


class Capture:
    def __init__(self):
        """Initializes this Capture object's main thread."""

        self.thread = threading.Thread(target=Capture._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\nStarted Capture.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly Capture screenshots of computer.
        :return:    None
        """
        config.frames = deque(maxlen=10)
        tmp_time = time.time()
        with mss.mss() as sct:
            while True:
                now_time = time.time()
                if now_time - tmp_time > 300:
                    header_monitor = {'top': br[1] - 31, 'left': config.MONITOR["left"], 'width': 1366, 'height': 31}
                    header_frame = np.array(sct.grab(header_monitor))
                    header_gray = cv2.cvtColor(header_frame, cv2.COLOR_BGR2GRAY)
                    if not utils.image_same(header_gray, config.HEADER_TEMPLATE):
                        cv2.imwrite('./logs/debug/header/{}.jpg'.format(now_time), header_frame)
                        print("WARN: the screen has been shifted, now cropped again")
                    config.cropped = False
                    config.MONITOR = {'top': 0, 'left': 0, 'width': 1400, 'height': 800}
                frame = np.array(sct.grab(config.MONITOR))
                if not config.cropped:
                    # crop the monitor to the game windows
                    tl, br = utils.single_match(frame[:frame.shape[0] // 8,
                                                :],
                                                config.HEADER_TEMPLATE)
                    config.MONITOR = {'top': br[1], 'left': tl[0], 'width': 1366, 'height': 768}
                    config.cropped = True
                    config.calibrated = False
                    tmp_time = time.time()
                else:
                    config.frames.append(frame)
