"""The main engine for OOEngine. Most other commands are called from here."""
import random
import sys
import copy
import pickle

import re

try:
    import commands
except ImportError:
    from . import commands

## Constants
RANDOM = copy.copy(random.randint(1, 2))
## End Constants


class Room:
    """A class for a room, with exits, a description, and a short name."""

    def __init__(self, items, description, short, exits, looks=None):
        self.items = items
        self.description = description
        self.short = short
        self.exits = exits
        self.locked = {}
        self.key = -1
        if looks is None:
            self.looks = {}
        else:
            self.looks = looks


class Item:
    """An item, with a name, a short name, and descriptions for when it is on the floor,
    and in the inventory."""

    def __init__(self, name, on_floor, short, long):
        self.name = name
        self.on_floor = on_floor
        self.short = short
        self.long = long
        self.messages = {
            "take": "You take the item.",
            "drop": "You drop the item.",
        }

    def eat(self):
        """Called when an item is eaten."""
        if self.messages["eat"] is not None:
            print(self.messages["eat"])

    def take(self):
        """Called when an item is taken."""
        if self.messages["take"] is not None:
            print(self.messages["take"])

    def drop(self):
        """Called when an item is dropped."""
        if self.messages["drop"] is not None:
            print(self.messages["drop"])


class Player:
    """A player for the game. Has a room, an inventory, and a name."""

    def __init__(self):
        self.room = 0
        self.inventory = []
        self.name = "Adventurer"


class Command:
    """A command for the game."""

    def __init__(self, function, helps):
        self.function = function
        self.helps = helps


class Game:
    """The object for the entire game."""

    def __init__(self):
        self.rooms = []
        self.player = Player()
        self.alive = True
        self.prompt = "> "
        self.commands = {}
        self.items = []
        self.intro = "Welcome to OOEngine!"
        self.ending = "\nGame ended."
        self.aliases = {
            "l": "look",
            "grab": "take",
            "up": "u",
            "down": "d",
            "get": "take",
            "i": "inventory",
            "g": "take",
            "talk": "look"
        }
        self.help_text = """# How to Play
To play OOEngine, you can use commands to influence the world around you. Use the 
commands north, east, south, and west to move around, with "go somewhere" to go a 
specific place.

Command List
help
quit
north (n)
east (e)
south (s)
west (w)
look [object]
take [item]
eat [item]
inventory (i)
go [direction]
info
infogen"""
        self.__version__ = "0.2.1"
        self.modpack_name = "OOEngine"
        self.mods = ["OOEngine"]
        self.mod_versions = [self.__version__]
        self.mod_helps = [self.help_text]
        self.branch_creator = "TheMadPunter"
        self.python_version = sys.version
        self.acknowledgements = """Willie Crowther and Don Woods for Colossal Cave.\n"""
        self.other = """"""
        self.debug = False

    def print_help_text(self):
        """Print help text."""
        print()
        print(self.help_text)
        print()

    def _info(self):
        info_string = """"""
        info_string += f"# {self.modpack_name} Info\n\n"
        info_string += f"## {self.modpack_name} version {self.__version__}\n"
        info_string += f"Python version {self.python_version}\n"
        info_string += f"Branch by {self.branch_creator}\n"
        for ident, info_help in enumerate(self.mod_helps):
            info_string += f"## {self.mods[ident]} version {self.mod_versions[ident]}\n"
            info_string += info_help + "\n"
            info_string += "\n"

        info_string += f"# acknowledgements: \n{self.acknowledgements}\n"
        info_string += self.other
        info_string += f"\nDebug: {str(self.debug)}"
        info_string = re.sub("\n", "\n\n", info_string)
        return info_string

    def info(self):
        """Print info."""
        print(self._info())

    def info_file(self):
        """Generate a readme file for the modpack."""
        with open("README.md", "w", encoding="utf-8") as file:
            file.write(self._info())

    def parse_command(self, command):
        """Parse a command from the command variable."""
        cmd_raw = command
        if cmd_raw is None:
            raise NameError
        split = command.split(" ")
        giirn = commands.get_items_in_room_names(self, self.player.room)
        split[0] = split[0].lower()
        if split[0] in self.aliases:
            split[0] = self.aliases[split[0]]
        if split[0] == "quit":
            self.alive = False

        elif split[0] == "help":
            self.print_help_text()

        elif split[0] == "n" or split[0] == "north":
            if "n" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["n"]
            else:
                print("You can't go that way!")

        elif split[0] == "e" or split[0] == "east":
            if "e" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["e"]
            else:
                print("You can't go that way!")

        elif split[0] == "w" or split[0] == "west":
            if "w" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["w"]
            else:
                print("You can't go that way!")

        elif split[0] == "s" or split[0] == "south":
            if "s" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["s"]
            else:
                print("You can't go that way!")

        elif split[0] == "d":
            if "d" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["d"]
            else:
                print("You can't go that way!")

        elif split[0] == "u":
            if "u" in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits["u"]
            else:
                print("You can't go that way!")

        elif split[0] == "go":
            if len(split) != 2:
                print("Go where?")
            if split[1] in self.rooms[self.player.room].exits:
                self.player.room = self.rooms[self.player.room].exits[split[1]]
            else:
                print("You can't go there!")

        elif split[0] == "look" or split[0] == "l":
            commands.look(split, self)

        elif split[0] == "take":
            self = commands.grab(split, self)

        elif split[0] == "drop":
            self = commands.drop(split, self)

        elif split[0] == "eat":
            self = commands.eat(split, self)

        elif split[0] == "inventory":
            self = commands.inventory(self, split)

        elif split[0] == "unlock":
            self = commands.unlock(self, split)

        elif split[0] == "info":
            self.info()

        elif split[0] == "infogen":
            self.info_file()
            print("Generated README.md file.")

        # elif split[0] == "save":
        #     try:
        #         with open(split[1], "wb") as loadfile:
        #             self = pickle.dump(self, loadfile, pickle.HIGHEST_PROTOCOL)
        #     except (FileNotFoundError):
        #         print("Oops! Can't load.")

        elif split[0] in self.commands:
            self = self.commands[split[0]](self, split)

        elif len(split) > 1:
            try:
                if split[1] in giirn:
                    if split[0] in self.items[giirn[split[1]]].__dict__:
                        self = self.items[giirn[split[1]]].__dict__[split[0]](
                            self, split
                        )
                        print("Done.")
                    else:
                        print(f"You can't {split[0]} this.")
                else:
                    print('Invalid command. Use "help" for help.')
            except IndexError:
                print(f"You can't {split[0]} this.")

        else:
            print('Invalid command. Use "help" for help.')

    def start(self):
        """Start the game."""
        try:
            print(self.intro)
            last_room = -1
            while self.alive:
                if self.player.room != last_room:
                    commands.look(["look"], self)
                    last_room = self.player.room
                command = input(self.prompt)
                self.parse_command(command)
        except KeyboardInterrupt:
            self.parse_command("quit")
        print(self.ending)


# pylint: disable=C0103
