import config
import time
import threading
from vkeys import press
import utils
import numpy as np
import cv2


def bar_to_per(img):
    img_mean = np.mean(img[:, :, 0:3], axis=0).reshape(10, 17, 3).mean(axis=1)
    dis = np.sum((img_mean - np.array([119, 113, 115])) ** 2, axis=1)
    # print(dis)
    for i in range(len(dis)):
        if dis[i] < 1000:
            break
    return i / len(dis)


class Pet:
    def __init__(self):
        """Initializes this Pet object's main thread."""

        self.thread = threading.Thread(target=Pet._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts the Pet.
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
            Pet._get_status()
            Pet._recovery()
            time.sleep(1)

    @staticmethod
    def _get_status():
        frame = config.frames[-1]
        hp_img = frame[716:728, 611:781, :]
        config.player_status["hp"] = bar_to_per(hp_img)
        mp_img = frame[732:744, 611:781, :]
        config.player_status["mp"] = bar_to_per(mp_img)
        # print(config.player_status)
        # cv2.imwrite("hp.jpg", hp_img)
        # cv2.imwrite("mp.jpg", mp_img)
        # time.sleep(10000)

    @staticmethod
    @utils.run_if_enabled
    def _recovery():

        if config.player_status["hp"] < 0.5:
            print("hp is ", config.player_status["hp"], "add hp")
            press("home", 1)
        if config.player_status["mp"] < 0.2:
            print("mp is ", config.player_status["mp"], "add mp")
            press("2", 1)
        time.sleep(5)