import time

from src import config
from src.vkeys import press

config.enabled=True
time.sleep(5)
print("press")
press("home", 1)
