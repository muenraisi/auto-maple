from vkeys import click
import time
import win32api
while True:
    print("click")
    position = [500,1000]
    win32api.SetCursorPos(position)
    # click([1000,1000],"left")
    time.sleep(10)