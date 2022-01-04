import time
import numpy as np
import cv2


def bar_to_per(rgb):
    rgb_mean = np.mean(rgb, axis=0).reshape(10, 17, 3).mean(axis=1)
    dis = np.sum((rgb_mean - np.array([119, 113, 115])) ** 2, axis=1)
    print(dis)
    for i in range(len(dis)):
        if dis[i] < 100:
            break
    return i / len(dis)


img = cv2.imread('temp.jpg')
# cv2.imshow("hp&mp", img)
hp = img[732:744, 611:781]
cv2.imwrite("test.jpg", hp)
hp_mean = bar_to_per(hp)
print(hp_mean)

# time.sleep(60)
