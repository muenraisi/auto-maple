"""The center of Auto Kanna that ties all the modules together."""

import config
import time
from camera import Camera
from capture import Capture
from listener import Listener
from bot import Bot
from pet import Pet


camera = Camera()
camera.start()

cap = Capture()
cap.start()

# Wait for the video capture to initialize
while not config.ready:
    time.sleep(0.01)

config.ready = False

listener = Listener()
listener.start()

bot = Bot()
bot.start()

pet = Pet()
pet.start()



while not config.ready:
    time.sleep(0.01)

print('\nSuccessfully initialized Auto Maple, now accepting commands.')

# Periodically save changes to the active Layout if it exists
while True:
    if config.layout:
        config.layout.save()
    time.sleep(5)
