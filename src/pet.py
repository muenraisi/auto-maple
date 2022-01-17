from src import config, utils
import time
import threading
import numpy as np
import cv2
from os import listdir
from os.path import isfile, join


def bar_to_per(img):
    img_mean = np.mean(img[:, :, 0:3], axis=0).reshape(10, 17, 3).mean(axis=1)
    dis = np.sum((img_mean - np.array([119, 113, 115])) ** 2, axis=1)
    # print(dis)
    for i in range(len(dis)):
        if dis[i] < 200:
            break
    return i / len(dis)


class Pet:
    def __init__(self):
        """Initializes this Pet object's main thread."""
        self.feed_time = time.time()
        self.thread = threading.Thread(target=self.main())
        self.thread.daemon = True

    def start(self):
        """
        Starts the Pet.
        :return:    None
        """

        print('\nStarted Pet.')
        self.thread.start()

    def main(self):
        """
        Constantly simulates the action of a pet.
        :return:    None
        """

        while True:
            if config.player_career:
                break
            else:
                time.sleep(1)
        # dir = "./career/"+ config.player_career + "/cooldown"
        # cooldown_files = [f for f in listdir(dir) if isfile(join(dir, f)) and "jpg" in f]

        while True:
            Pet._check_status()
            self.feed()

    @staticmethod
    @utils.run_if_enabled
    def _check_status():
        frame = config.frames[-1]
        hp_img = frame[716:728, 611:781, :]
        config.player_status["hp"] = bar_to_per(hp_img)
        mp_img = frame[732:744, 611:781, :]
        config.player_status["mp"] = bar_to_per(mp_img)
        # print(config.player_status)
        # cv2.imwrite("hp.jpg", hp_img)
        # cv2.imwrite("mp.jpg", mp_img)
        # time.sleep(10000)

        if config.player_status["hp"] < 0.4:
            print("hp is ", config.player_status["hp"], "prepare to add hp")
            utils.insert_player_command("home", 1)
            now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
            cv2.imwrite('./assets/debug/hp/{}.jpg'.format(now_time), frame)

        if config.player_status["mp"] < 0.2:
            print("mp is ", config.player_status["mp"], "prepare to add mp")
            utils.insert_player_command("2", 1)
            now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
            cv2.imwrite('./assets/debug/mp/{}.jpg'.format(now_time), frame)

    @utils.run_if_enabled
    def feed(self):
        if time.time() - self.feed_time > 900:
            utils.insert_player_command("6", 1)
            self.feed_time = time.time()

    @utils.run_if_enabled
    def cooldown(self):
        pass
    # @staticmethod
    # @utils.run_if_enabled
    # def _periodic_skill():
    #     for
