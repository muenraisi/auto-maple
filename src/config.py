"""A collection of variables shared across multiple modules."""

import cv2
import wmi

# import ctypes
# user32 = ctypes.windll.user32
#
# SCREENSIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

RESOLUTION = (1920, 1080)
#################################
#           CONSTANTS           #
#################################
# Describes the dimensions of the screen to capture with mss
# MONITOR = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}

FULL_MONITOR = {'top': 0, 'left': 0, 'width': RESOLUTION[0], 'height': RESOLUTION[1]}

MONITOR = None

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 4

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 8


DEBUG=True
#################################
#           TEMPLATES           #
#################################

# alert music
ALERT_MUSIC = "恭喜发财.mp3"

# The bottom right corner of the minimap
MINIMAP_TEMPLATE_BR = cv2.imread('assets/minimap_br.jpg', 0)
# The topper left corner of the minimap
MINIMAP_TEMPLATE_TL = cv2.imread('assets/minimap_tl.jpg', 0)

#
HEADER_TEMPLATE = cv2.imread('assets/header_template.jpg', 0)

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)

# the bonus square on the screen
BONUS_TEMPLATE = cv2.imread("assets/bonus_template.jpg", 0)

# the dialogue box on the screen
DIALOGUE_TEMPLATE = cv2.imread("assets/dialogue_template.jpg", 0)

# A rune's symbol on the minimap
RUNE_TEMPLATE = cv2.imread('assets/rune_template.png', 0)

RUNE_COOLDOWN_TEMPLATE = cv2.imread('assets/rune_cooldown_template.jpg', 0)
# The icon of the buff given by the rune
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template.jpg', 0)

# The Mushroom princess checking
MUSHROOM_TEMPLATE = cv2.imread('assets/mushroom_template.jpg', 0)

#################################
#       Global Variables        #
#################################
#
# the player's career
player_career = None

player_skills = {}

# the player's command
player_commands = []

player_command_lock = False

#
player_status = {"hp": 100, "mp": 100}

# The player's position relative to the minimap
player_pos = (0, 0)

# Describes whether the bot is currently running or not
enabled = False

# Describes whether the bot has been successfully initialized
ready = False

# Describes whether the video capture has calibrated the minimap
calibrated = False

# Describes whether the keyboard listener is currently running
listening = False

# The ratio of the minimap's width divided by its height (used for conversions)
mm_ratio = 1

# Describes whether a rune has appeared in the game
rune_active = False

# The position of the rune relative to the minimap
rune_pos = (0, 0)

# The location of the Point object that is closest to the rune
rune_index = (0, 0)

# Indicates whether a danger has been detected (Elite Boss, room change, etc)
alert_active = False

# screenshot
frames = None

# Stores all the Points and labels in the current user-defined routine
sequence = []

# Represents the index that the bot is currently at
seq_index = 0

# Represents the current shortest path that the bot is taking
path = []

# Stores a map of all available commands that can be used by routines
command_book = {}

# Stores the name of the current routine file
routine = None

# Stores the Layout object associated with the current routine
layout = None

# remember last time checking bonus box
last_checking_click = 0

#################################
#       Routine Settings        #
#################################
# The allowed error from the destination when moving towards a Point
move_tolerance = 0.1

# The allowed error from a specific location while adjusting to that location
adjust_tolerance = 0.01

# Whether the bot should save new player positions to the current layout
record_layout = False

# The amount of time (in seconds) to wait between each call to the 'buff' command
buff_cooldown = 180

#################################
#      Keyboard Settings        #
#################################

KEYBOARD_JUMP = "alt"

#################################
#       Precompute Vars         #
#################################


computer_name = wmi.WMI().Win32_ComputerSystem()[0].name
print(computer_name)