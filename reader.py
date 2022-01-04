"""A module for tracking useful in-game information."""

import config
import mss
import cv2
import threading
import numpy as np
import utils
import time
from bot import Point
from vkeys import click


class Reader:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Reader object's main thread."""

        self.thread = threading.Thread(target=Reader._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Reader's thread.
        :return:    None
        """

        print('\nStarted video reader.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly monitors the player's position and in-game events.
        :return:    None
        """

        while True:
            if not config.cropped or len(config.frames) == 0:
                time.sleep(0.01)
                continue
            frame = config.frames[-1]
            if not config.calibrated:
                tl, _ = utils.single_match(frame[:frame.shape[0] // 4,
                                           :frame.shape[1] // 3],
                                           config.MINIMAP_TEMPLATE_TL)
                mm_tl = (tl[0] + 8, tl[1] + 20)  # minimap top left

                # Get the bottom right corner of the minimap
                _, br = utils.single_match(frame[:frame.shape[0] // 4,
                                           :frame.shape[1] // 3],
                                           config.MINIMAP_TEMPLATE_BR)
                mm_br = tuple(max(75, x - config.MINIMAP_BOTTOM_BORDER) for x in br)  # minimap bot right
                config.mm_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])

                config.calibrated = True
                config.ready = True
            else:
                #####################################
                #       Monitor in-game events      #
                #####################################
                height, width, _ = frame.shape

                # Check for unexpected black screen regardless of whether bot is enabled
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if config.enabled and not config.alert_active \
                        and np.count_nonzero(gray < 15) / height / width > 0.95:
                    config.alert_active = True
                    config.enabled = False

                # Check for elite warning
                elite_frame = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
                elite = utils.multi_match(elite_frame, config.ELITE_TEMPLATE, threshold=0.9)
                if config.enabled and not config.alert_active and elite:
                    config.alert_active = True
                    config.enabled = False

                # Check for mushroom princess # TODO: 在完成自动识别后取消
                mushroom_frame = frame[height // 2: height, 3 * width // 4:width]
                elite = utils.multi_match(mushroom_frame, config.MUSHROOM_TEMPLATE, threshold=0.9)
                if config.enabled and not config.alert_active and elite:
                    config.alert_active = True
                    config.enabled = False

                # Crop the frame to only show the minimap
                minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                player = utils.multi_match(minimap, config.PLAYER_TEMPLATE, threshold=0.8)
                if player:
                    config.player_pos = utils.convert_to_relative(player[0], minimap)

                # Check for a rune
                if not config.rune_active:
                    rune = utils.multi_match(minimap, config.RUNE_TEMPLATE, threshold=0.9)
                    if rune:
                        config.alert_active = True
                        continue
                    if rune and config.sequence:
                        config.pet_active = False
                        abs_rune_pos = (rune[0][0] - 1, rune[0][1])
                        config.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                        distances = list(map(Reader._distance_to_rune, config.sequence))
                        index = np.argmin(distances)
                        config.rune_index = config.sequence[index].location
                        config.rune_active = True

                # TODO: to avoid action in capture
                now = time.time()
                if now - config.last_checking_click > 20:
                    # bonus box
                    bonus = utils.multi_match(frame, config.BONUS_TEMPLATE, threshold=0.8)
                    if bonus:
                        print("detect bonus box")
                        for _ in range(3):
                            click((bonus[0][1] + config.MONITOR["left"], bonus[0][0] + config.MONITOR["top"]))
                    # dialogue box
                    dialogue = utils.multi_match(frame, config.DIALOGUE_TEMPLATE, threshold=0.8)
                    if dialogue:
                        print("detect dialogue box")
                        for _ in range(3):
                            click((dialogue[0][1] + config.MONITOR["left"], dialogue[0][0] + config.MONITOR["top"]))
                    config.last_checking_click = now

                #########################################
                #       Display useful information      #
                #########################################
                minimap = Reader._rescale_frame(minimap, 2.5)

                # Mark the position of the active rune
                if config.rune_active:
                    cv2.circle(minimap,
                               utils.convert_to_absolute(config.rune_pos, minimap),
                               5,
                               (128, 0, 128),
                               -1)

                # Draw the current path that the program is taking
                path = config.path
                if config.enabled and len(path) > 1:
                    for i in range(len(path) - 1):
                        start = utils.convert_to_absolute(path[i], minimap)
                        end = utils.convert_to_absolute(path[i + 1], minimap)
                        cv2.line(minimap, start, end, (255, 255, 0), 1)

                # Draw each Point in the routine as a circle
                for p in config.sequence:
                    Reader._draw_point(minimap,
                                       p,
                                       (0, 255, 0) if config.enabled else (0, 0, 255))

                # Display the current Layout
                if config.layout:
                    config.layout.draw(minimap)

                # Draw the player's position on top of everything
                cv2.circle(minimap,
                           utils.convert_to_absolute(config.player_pos, minimap),
                           3,
                           (255, 0, 0),
                           -1)
                winname = 'minimap'
                cv2.namedWindow(winname)  # Create a named window
                cv2.moveWindow(winname, 1400, 30)  # Move it to (1400,30)
                cv2.imshow('minimap', minimap)
            if cv2.waitKey(1) & 0xFF == 27:  # 27 is ASCII for the Esc key
                break

    @staticmethod
    def _count(frame, threshold):
        """
        Counts the number of pixels in FRAME that are less than or equal to THRESHOLD.
        Two pixels are compared by their corresponding tuple elements in order.
        :param frame:       The image in which to search.
        :param threshold:   The pixel value to compare to.
        :return:            The number of pixels in FRAME that are below THRESHOLD.
        """

        count = 0
        for row in frame:
            for col in row:
                pixel = frame[row][col]
                if len(pixel) == len(threshold):
                    valid = True
                    for i in range(len(pixel)):
                        valid = valid and frame[i] <= threshold[i]
                    if valid:
                        count += 1
        return count

    @staticmethod
    def _distance_to_rune(point):
        """
        Calculates the distance from POINT to the rune.
        :param point:   The position to check.
        :return:        The distance from POINT to the rune, infinity if it is not a Point object.
        """

        if isinstance(point, Point):
            return utils.distance(config.rune_pos, point.location)
        return float('inf')

    @staticmethod
    def _draw_point(minimap, point, color):
        """
        Draws a visual representation of POINT onto MINIMAP. The radius of the circle represents
        the allowed error when moving towards POINT.
        :param minimap:     The image on which to draw.
        :param point:       The location of the Point object to depict.
        :param color:       The color of the circle.
        :return:            None
        """

        if isinstance(point, Point):
            center = utils.convert_to_absolute(point.location, minimap)
            cv2.circle(minimap,
                       center,
                       round(minimap.shape[1] * config.move_tolerance),
                       color,
                       1)

    @staticmethod
    def _rescale_frame(frame, percent=1.0):
        """
        Proportionally rescales the width and height of FRAME by PERCENT.
        :param frame:       The image to rescale.
        :param percent:     The percentage by which to rescale.
        :return:            The resized image.
        """

        width = int(frame.shape[1] * percent)
        height = int(frame.shape[0] * percent)
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
