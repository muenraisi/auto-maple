import numpy as np
import os, cv2

# import tensorflow as tf

crop_state = True
filter_color_state = True
canny_state = True
crop_arrows_state =True


def filter_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 100, 100), (25, 255, 255))

    # Slice the mask
    imask = mask > 0
    arrows = np.zeros_like(image, np.uint8)
    arrows[imask] = image[imask]
    return arrows


def canny(image):
    height, width, channels = image.shape
    image = cv2.Canny(image, 200, 300)
    # cropped = image[:height//2,width//4:3*width//4]
    colored = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return colored


img = cv2.imread("test.jpg")
height, width, channels = img.shape
if crop_state:
    img = img[:height // 2, width // 3:2 * width // 3]
# if filter_color_state:
#     img = filter_color(img)
# if canny_state:
#     image = canny(img)
# img = cv2.GaussianBlur(img, (5, 5), 0)

hsv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2HSV)
hue = hsv[:, :, 0]

cv2.imwrite("temp.jpg", hue)