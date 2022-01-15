"""The center of Auto Kanna that ties all the modules together."""

from src import config
import time
from src.capture import Capture
from src.reader import Reader
from src.presser import Presser
from src.listener import Listener
from src.bot import Bot
from src.picker import Picker
from src.pet import Pet

capture = Capture()
capture.start()

reader = Reader()
reader.start()

# Wait for the video capture to initialize
while not config.ready:
    time.sleep(0.01)

config.ready = False

listener = Listener()
listener.start()

pet = Pet()
pet.start()

bot = Bot()
bot.start()

picker = Picker()
picker.start()

while not config.ready:
    time.sleep(0.01)

print('\nSuccessfully initialized Auto Maple, now accepting commands.')

# Periodically save changes to the active Layout if it exists
while True:
    if config.layout:
        config.layout.save()
    time.sleep(5)
