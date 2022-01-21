import cv2
import mss
from src import config
from collections import deque
from src import bot
from src import  utils
import time
import numpy as np
from os import listdir
from os.path import isfile, join


bot = bot.Bot()
bot.start()

config.enabled = True

config.frames = deque(maxlen=10)
config.player_career = "kanna"
tmp_time = time.time()
shortcuts={}

career = ''.join([i for i in config.player_career if not i.isdigit()])
dir = "./career/" + config.computer_name + "/" + career
jpg_files = [f for f in listdir(dir) if isfile(join(dir, f)) and "jpg" in f]
shortcut_files = [item for item in jpg_files if item.startswith("shortcut_")]
for file in shortcut_files:
    _ = file.find(".")
    key = file[9:_]
    shortcuts[key] = cv2.imread(dir + "/" + file, 0)

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        shortcut_area = gray[687:687 + 69, 805:805 + 559]
        now_time = time.strftime('%Y%m%d%H%M', time.localtime())
        cv2.imwrite('./logs/debug/shortcuts/area_{}.jpg'.format(now_time), shortcut_area)
        for key, value in config.player_skills.items():
            print(key,value)
            if value["cooldown"]:
                h, w = SHORTCUT_MAP[key]
                now_shortcut = shortcut_area[35 * h + 4:35 * h + 30, 35 * w + 4:35 * w + 30]
                cv2.imwrite('./logs/debug/shortcuts/{}_{}.jpg'.format(key, now_time), now_shortcut)
                if utils.image_same(now_shortcut, shortcuts[key]):
                    print("same")
                    utils.insert_player_command(key, 1, down_time=value["down_time"], up_time=value["up_time"])
                else:
                    print("skill ", key, "at", now_time, "is still cooldown")
