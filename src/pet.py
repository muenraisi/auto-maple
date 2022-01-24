from src import config, utils
import time
import threading
import numpy as np
import cv2
from os import listdir
from os.path import isfile, join

SHORTCUT_MAP = {
    "q": (0, 0),
    "w": (0, 1),
    "e": (0, 2),
    "r": (0, 3),
    "t": (0, 4),
    "f1": (0, 5),
    "f2": (0, 6),
    "f3": (0, 7),
    "f4": (0, 8),
    "1": (0, 9),
    "2": (0, 10),
    "3": (0, 11),
    "4": (0, 12),
    "5": (0, 13),
    "home": (0, 14),
    "pageup": (0, 15),
    "a": (1, 0),
    "s": (1, 1),
    "d": (1, 2),
    "f": (1, 3),
    "g": (1, 4),
    "f5": (1, 5),
    "f6": (1, 6),
    "f7": (1, 7),
    "f8": (1, 8),
    "z": (1, 9),
    "x": (1, 10),
    "c": (1, 11),
    "v": (1, 12),
    "b": (1, 13),
    "end": (1, 14),
    "pagedown": (1, 15),
}


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
        self.shortcuts = {}
        self.thread = threading.Thread(target=self.main())
        self.thread.daemon = True

    def start(self):
        """
        Starts the Pet.
        :return:    None
        """

        print('\nStarted Pet main.')
        self.thread.start()

    def main(self):
        """
        Constantly simulates the action of a pet.
        :return:    None
        """
        career = ''.join([i for i in config.player_career if not i.isdigit()])
        dir = "./career/" +career
        jpg_files = [f for f in listdir(dir) if isfile(join(dir, f)) and "jpg" in f]
        shortcut_files = [item for item in jpg_files if item.startswith("shortcut_")]
        for file in shortcut_files:
            _ = file.find(".")
            key = file[9:_]
            self.shortcuts[key] = cv2.imread(dir + "/" + file, 0)

        print('\nStarted Pet loop.')
        while True:
            if len(config.frames)!=0:
                Pet._check_status()
                self.feed()
                self.cooldown()
                time.sleep(1)

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
            utils.insert_player_command("home", down_time=0.2)
            now_time = time.strftime('%Y%m%d%H%M', time.localtime())
            cv2.imwrite('./logs/debug/hp/{}_{}.jpg'.format(now_time, config.player_status["hp"]), frame)

        if config.player_status["mp"] < 0.2:
            print("mp is ", config.player_status["mp"], "prepare to add mp")
            utils.insert_player_command("2", down_time=0.2)
            now_time = time.strftime('%Y%m%d%H%M', time.localtime())
            cv2.imwrite('./logs/debug/mp/{}_{}.jpg'.format(now_time, config.player_status["mp"]), frame)

    @utils.run_if_enabled
    def feed(self):
        if time.time() - self.feed_time > 900:
            utils.insert_player_command("6", down_time=0.2)
            self.feed_time = time.time()

    @utils.run_if_enabled
    def cooldown(self):
        if not config.frames:
            return
        frame = config.frames[-1]
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        shortcut_area = frame[687:687 + 69, 805:805 + 559]
        now_time = time.strftime('%Y%m%d%H%M', time.localtime())
        cv2.imwrite('./logs/debug/shortcuts/area_{}.jpg'.format(now_time), shortcut_area)
        for key, value in config.player_skills.items():
            if value["cooldown"]:
                h, w = SHORTCUT_MAP[key]
                now_shortcut = shortcut_area[35 * h + 4:35 * h + 30, 35 * w + 4:35 * w + 30]
                cv2.imwrite('./logs/debug/shortcuts/{}_{}.jpg'.format(key, now_time), now_shortcut)
                if utils.multi_match(shortcut_area, self.shortcuts[key], threshold = 0.95):
                # if utils.image_same(now_shortcut, self.shortcuts[key]):
                    utils.insert_player_command(key, down_time=value["down_time"], up_time=value["up_time"])

    # @staticmethod
    # @utils.
    # def _periodic_skill():
    #     for
