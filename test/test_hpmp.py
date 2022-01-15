from src import pet
import cv2
from src.pet import bar_to_per

img_name = "Maple_220115_102543.jpg"

frame = cv2.imread("screenshots/" + img_name)

hp_img = frame[716:728, 611:781, :]

mp_img = frame[732:744, 611:781, :]

player_status = {"hp": bar_to_per(hp_img), "mp": bar_to_per(mp_img)}
print(player_status)
