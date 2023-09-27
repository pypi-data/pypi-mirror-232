import sys
import time
import keyboard
import ctypes
import os

class ilollekhelperlib:

    def slowPrint(text: str):
        """Prints text with a typewriter effect, with an optional delay between characters. Idea from textutils.slowPrint() from ComputerCraft."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.047)
        print()  # Print a newline at the end

    def fastPrint(text: str):
        """Prints text with a typewriter effect, with an optional delay between characters. Idea from textutils.slowPrint() from ComputerCraft."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.025)
        print()  # Print a newline at the end

    def adjustablePrint(text: str, delay: float):
        """Prints text with a typewriter effect, with an optional delay between characters. Idea from textutils.slowPrint() from ComputerCraft."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()  # Print a newline at the end

    def clear():
    """Clears the System - Should be OS Cross-Compatible."""
        # check and make call for specific operating system
    os.system('cls' if os.name == 'nt' else 'clear')

    def set_cursor_pos(x, y):
        """Sets Position where to print like in ComputerCraft's term.setCursorPos()"""
        handle = ctypes.windll.kernel32.GetStdHandle(-11)  # Get handle to standard output (console)
        coords = ctypes.wintypes._COORD(x, y)
        ctypes.windll.kernel32.SetConsoleCursorPosition(handle, coords)

    def draw_gui(options: list):
        """Draws a small GUI for Console/CLI Applications. Interaction with UP and DOWN arrow keys, and ENTER. Returns Index of option (integer) and requires a List of Elements on the Menu."""
        menu = options
        option = 0
        counter = 0

        while True:
            for element in menu:
                set_cursor_pos(0, counter)
                if option == counter:
                    print(f'> {element[0]}', end='\r')
                else:
                    print(f'  {element[0]}', end='\r')
                counter += 1
            key = keyboard.read_event()
            if keyboard.is_pressed("down"):
                if option != len(menu) - 1:
                    option += 1
            elif keyboard.is_pressed("up"):
                if option != 0:
                    option -= 1
            elif keyboard.is_pressed("enter"):
            clear()
            return option
            counter = 0