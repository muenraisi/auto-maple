"""An interpreter that reads and executes user-created routines."""

from src import config, utils, detection, commands
import threading
import winsound
import time
import csv
import pygame
import inspect
import keyboard as kb
import cv2
from os import listdir, makedirs
from os.path import isfile, join, splitext
from src.vkeys import press, click, execute_skill
from layout import Layout

# A dictionary that maps each setting to its validator function
SETTING_VALIDATORS = {'move_tolerance': float,
                      'adjust_tolerance': float,
                      'record_layout': utils.validate_boolean,
                      'buff_cooldown': int}


class Point:
    """Represents a location in a user-defined routine."""

    def __init__(self, x, y, frequency=1, counter=0, adjust='False'):
        self.location = (float(x), float(y))
        self.frequency = utils.validate_nonzero_int(frequency)
        self.counter = int(counter)
        self.adjust = utils.validate_boolean(adjust)
        self.commands = []

    @utils.run_if_enabled
    def execute(self):
        """
        Executes the set of actions associated with this Point.
        :return:    None
        """

        if self.counter == 0:
            if config.enabled:
                print()
                print(self._heading())
            move = config.command_book.get('move')
            move(*self.location).execute()
            if self.adjust:
                adjust = config.command_book.get('adjust')
                adjust(*self.location).execute()
            for command in self.commands:
                command.execute()
        self._increment_counter()

    @utils.run_if_enabled
    def _increment_counter(self):
        """
        Increments this Point's counter, wrapping back to 0 at the upper bound.
        :return:    None
        """

        self.counter = (self.counter + 1) % self.frequency

    def __str__(self):
        """
        Returns a string representation of this Point object.
        :return:    This Point's string representation.
        """

        result = self._heading()
        for command in self.commands:
            result = result + '\n' + str(command)
        return result

    def _heading(self):
        """
        Returns this Point's heading for display purposes.
        :return:    This Point's heading.
        """

        return f'From ({round(config.player_pos[0], 3)}, {round(config.player_pos[1], 3)}) to point at  {self.location}' + (':' if self.commands else '')


class Bot:
    """A class that interprets and executes user-defined routines."""

    alert = None

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        pygame.mixer.init()
        Bot.alert = pygame.mixer.music
        Bot.alert.load('./assets/'+config.ALERT_MUSIC)

        Bot.load_commands()
        Bot.load_routine()

        self.thread = threading.Thread(target=Bot._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        print('\nStarted main bot loop.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        # print('\nInitializing detection algorithm...\n')
        # model = detection.load_model()
        # print('\nInitialized detection algorithm.')

        config.listening = True
        buff = config.command_book['buff']()
        while True:
            if config.alert_active:
                Bot._alert()
            if config.enabled:
                if config.player_commands:
                    Bot._execute_skills()
                buff.main()  # TODO: buff function should be improved to ensure buff in time
                element = config.sequence[config.seq_index]
                if isinstance(element, Point):
                    element.execute()
                    if config.rune_active and element.location == config.rune_index:
                        print("发现符文")
                        config.alert_active = True
                        # Bot._solve_rune(model, sct)
                Bot._step()
            else:
                time.sleep(0.01)

    @staticmethod
    @utils.run_if_enabled
    def _solve_rune(model):
        """
        Moves to the position of the rune and solves the arrow-key puzzle.
        :param model:   The TensorFlow model to classify with.
        :return:        None
        """

        move = config.command_book.get('move')
        move(*config.rune_pos).execute()
        adjust = config.command_book.get('adjust')
        adjust(*config.rune_pos).execute()
        time.sleep(0.2)
        press('space', 1, down_time=0.2)  # Press 'space' to interact with rune in-game
        print('\nSolving rune:')
        inferences = []
        for _ in range(15):
            frame = config.frames[-1]
            solution = detection.merge_detection(model, frame)
            if solution:
                print(', '.join(solution))
                if solution in inferences:
                    print('Solution found, entering result.')
                    for arrow in solution:
                        press(arrow, 1, down_time=0.1)
                    time.sleep(1)
                    for _ in range(3):
                        time.sleep(0.3)
                        frame = config.frames[-1]
                        rune_buff = utils.multi_match(frame[:frame.shape[0] // 8, :],
                                                      config.RUNE_BUFF_TEMPLATE,
                                                      threshold=0.9)
                        if rune_buff:
                            rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                            click(rune_buff_pos, button='right')
                    break
                elif len(solution) == 4:
                    inferences.append(solution)
        config.rune_active = False
        time.sleep(0.5)
        if config.rune_active:
            config.alert_active = True

    @staticmethod
    def _alert():
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once 'insert' is pressed.
        :return:    None
        """
        config.enabled = False
        config.rune_active = False
        config.listening = False
        Bot.alert.play(-1)
        now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
        makedirs('./logs/alerts/{}'.format(now_time), exist_ok=False)
        count = 0
        while not kb.is_pressed('insert'):
            count += 1
            cv2.imwrite('./logs/alerts/{}/{}.jpg'.format(now_time, str(count).zfill(4)), config.frames[-1])
        Bot.alert.stop()
        config.alert_active = False
        time.sleep(1)
        config.listening = True

    @staticmethod
    @utils.run_if_enabled
    def _step():
        """
        Increments config.seq_index and wraps back to 0 at the end of config.sequence.
        :return:    None
        """

        config.seq_index = (config.seq_index + 1) % len(config.sequence)

    @staticmethod
    def load_commands():
        """
        Prompts the user to select a command module to import. Updates config's command book.
        :return:    None
        """

        utils.print_separator()
        print('~~~ Import career book ~~~')
        module_file = Bot._select_file('./career', '.py')
        config.player_career = splitext(module_file)[0]

        # Generate a command book using the selected module
        utils.print_separator()
        print(f"Loading career book '{config.player_career}'...")
        module = __import__(f'career.{config.player_career}', fromlist=[''])
        if "SKILLS" in [item for item in dir(module) if not item.startswith("__")]:
            config.player_skills = module.SKILLS
        config.command_book = {}
        for name, command in inspect.getmembers(module, inspect.isclass):
            name = name.lower()
            config.command_book[name] = command

        # Import common commands
        config.command_book['goto'] = commands.Goto
        config.command_book['wait'] = commands.Wait
        config.command_book['walk'] = commands.Walk
        config.command_book['fall'] = commands.Fall

        # Check if required commands have been implemented
        success = True
        for command in ['move', 'adjust', 'buff']:
            if command not in config.command_book:
                success = False
                print(f"Error: Must implement '{command}' command.")
        if success:
            print(f"Successfully loaded career book '{config.player_career}'.")
        else:
            config.command_book = {'move': commands.DefaultMove,
                                   'adjust': commands.DefaultAdjust,
                                   'buff': commands.DefaultBuff}
            print(f"Career book '{config.player_career}' was not loaded.")

    @staticmethod
    def load_routine(file=None):
        """
        Attempts to load FILE into a sequence of Points. Prompts user input if no file is given.
        :param file:    The file's path.
        :return:        None
        """

        routines_dir = './routines'
        if not file:
            utils.print_separator()
            print('~~~ Import Routine ~~~')
            file = Bot._select_file(routines_dir, '.csv')
        if file:
            config.calibrated = False
            config.sequence = []
            config.seq_index = 0
            utils.reset_settings()
            utils.print_separator()
            print(f"Loading routine '{file}'...")
            with open(join(routines_dir, file), newline='') as f:
                csv_reader = csv.reader(f, skipinitialspace=True)
                curr_point = None
                line = 1
                for row in csv_reader:
                    result = Bot._eval(row, line)
                    if result:
                        if isinstance(result, commands.Command):
                            if curr_point:
                                curr_point.commands.append(result)
                        else:
                            config.sequence.append(result)
                            if isinstance(result, Point):
                                curr_point = result
                    line += 1
            config.routine = file
            config.layout = Layout.load(file)
            winsound.Beep(523, 200)  # C5
            winsound.Beep(659, 200)  # E5
            winsound.Beep(784, 200)  # G5
            print(f"Finished loading routine '{file}'.")

    @staticmethod
    def _eval(expr, n):
        """
        Evaluates the given expression EXPR in the context of Auto Kanna.
        :param expr:    A list of strings to evaluate.
        :param n:       The line number of EXPR in the routine file.
        :return:        An object that represents EXPR.
        """

        if expr and isinstance(expr, list):
            first, rest = expr[0].lower(), expr[1:]
            args, kwargs = utils.separate_args(rest)
            line = f'Line {n}: '
            if first == '@':  # Check for labels
                if len(args) != 1 or len(kwargs) != 0:
                    print(line + 'Incorrect number of arguments for a label.')
                else:
                    return args[0]
            elif first == 's':  # Check for settings
                if len(args) != 2 or len(kwargs) != 0:
                    print(line + 'Incorrect number of arguments for a setting.')
                else:
                    variable = args[0].lower()
                    value = args[1].lower()
                    if variable not in SETTING_VALIDATORS:
                        print(line + f"'{variable}' is not a valid setting.")
                    else:
                        try:
                            value = SETTING_VALIDATORS[variable](value)
                            setattr(config, variable, value)
                        except ValueError:
                            print(line + f"'{value}' is not a valid value for '{variable}'.")
            elif first == '*':  # Check for Points
                try:
                    return Point(*args, **kwargs)
                except ValueError:
                    print(line + f'Invalid arguments for a Point: {args}, {kwargs}')
                except TypeError:
                    print(line + 'Incorrect number of arguments for a Point.')
            else:  # Otherwise might be a Command
                if first not in config.command_book.keys():
                    print(line + f"Command '{first}' does not exist.")
                else:
                    try:
                        return config.command_book.get(first)(*args, **kwargs)
                    except ValueError:
                        print(line + f"Invalid arguments for command '{first}': {args}, {kwargs}")
                    except TypeError:
                        print(line + f"Incorrect number of arguments for command '{first}'.")

    @staticmethod
    def _select_file(directory, extension):
        """
        Prompts the user to select a file from the .csv files within DIRECTORY.
        :param directory:   The directory in which to search.
        :param extension:   The file extension for which to filter by.
        :return:            The path of the selected file.
        """

        index = float('inf')
        valid_files = [f for f in listdir(directory) if isfile(join(directory, f)) and extension in f]
        num_files = len(valid_files)
        if not valid_files:
            print(f"Unable to find any '{extension}' files in '{directory}'.")
        else:
            print('Please select from the following files:\n')
            for i in range(num_files):
                print(f'{i:02} -- {valid_files[i]}')
            print()

            selection = 0
            while index not in range(num_files):
                try:
                    selection = input('>>> ')
                except KeyboardInterrupt:
                    exit()

                if not utils.validate_type(selection, int):
                    print('Selection must be an integer.')
                else:
                    index = int(selection)
                    if index not in range(num_files):
                        print(f'Please enter an integer between 0 and {max(0, num_files - 1)}.')
            return valid_files[index]

    @staticmethod
    def toggle_enabled():
        """
        Resumes or pauses the current routine. Plays a sound and prints a message to notify
        the user.
        :return:    None
        """
        config.rune_active = False
        config.alert_active = False
        utils.print_separator()
        print('#' * 18)
        print(f"#    {'DISABLED' if config.enabled else 'ENABLED '}    #")
        print('#' * 18)
        config.enabled = not config.enabled
        if config.enabled:
            config.pick_active = True
            winsound.Beep(784, 333)  # G5
        else:
            config.pick_active = False
            winsound.Beep(523, 333)  # C5

    @staticmethod
    @utils.run_if_enabled
    def _execute_skills():
        config.player_command_lock = True
        for command in config.player_commands:
            if config.DEBUG:
                print("press", command)
            execute_skill(*command[0], **command[1])
        config.player_commands = []
        config.player_command_lock = False
