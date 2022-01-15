from src.vkeys import click
import time
import win32api
height=1080
width =1920
a=(499, 516)
from src import config

config.enabled = True
while True:
    print("click")
    now_pos = win32api.GetCursorPos()
    print(now_pos)
    position = (int(a[0] * 0.8), int(a[1]*0.8))
    win32api.SetCursorPos(position)
    for _ in range(3):
        click(position,"left")
    time.sleep(5)