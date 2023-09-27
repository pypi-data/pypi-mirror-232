import random
import sys
import copy

import re

import commands

## Constants
## End Constants


class Room:
    def __init__(self, items, description, short, exits, looks=None):
        self.items = items
        self.description = description
        self.short = short
        self.exits = exits
        if looks == None:
            self.looks = {}
        else:
            self.looks = looks


class Item:
    def __init__(self, name, onFloor, short, long):
        self.name = name
        self.onFloor = onFloor
        self.short = short
        self.long = long
        self.messages = {
            "eat": "The ball is delicious.",
            "take": "You take the item.",
            "drop": "You drop the item.",
        }

    def eat(self):
        if self.messages["eat"] != None:
            print(self.messages["eat"])

    def take(self):
        if self.messages["take"] != None:
            print(self.messages["take"])

    def drop(self):
        if self.messages["drop"] != None:
            print(self.messages["drop"])


class Player:
    def __init__(self):
        self.room = 0
        self.inventory = []
        self.name = "Adventurer"


class Command:
    def __init__(self, function, help):
        self.function = function
        self.help = help


class Game:
    def __init__(self):
        self.rooms = []
        self.player = Player()
        self.alive = True
        self.prompt = "> "
        self.commands = {}
        self.items = []
        self.intro = "Welcome to OOEngine!"
        self.ending = "Game ended."
        self.aliases = {
            "l": "look",
            "grab": "take",
            "up": "u",
            "down": "d",
            "get": "take",
            "i": "inventory",
        }
        self.helpText = """# How to Play
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
        self.__version__ = "0.1.0"
        self.MODPACK_NAME = "OOEngine"
        self.MODS = ["OOEngine"]
        self.MOD_VERSIONS = [self.__version__]
        self.MOD_HELPS = [self.helpText]
        self.BRANCH_CREATOR = "TheMadPunter"
        self.PYTHON_VERSION = sys.version
        self.ACKNOWLEDGEMENTS = """Willie Crowther and Don Woods for Colossal Cave.\n"""
        self.OTHER = """"""
        self.DEBUG = False

    def help(self):
        print()
        print(self.helpText)
        print()

    def _info(self):
        infoString = """"""
        infoString += f"# {self.MODPACK_NAME} Info\n\n"
        infoString += f"## {self.MODPACK_NAME} version {self.__version__}\n"
        infoString += f"Python version {self.PYTHON_VERSION}\n"
        infoString += f"Branch by {self.BRANCH_CREATOR}\n"
        for id, infoHelp in enumerate(self.MOD_HELPS):
            infoString += f"## {self.MODS[id]} version {self.MOD_VERSIONS[id]}\n"
            infoString += infoHelp + "\n"
            infoString += "\n"

        infoString += f"# Acknowledgements: \n{self.ACKNOWLEDGEMENTS}\n"
        infoString += self.OTHER
        infoString += f"\nDebug: {str(self.DEBUG)}"
        infoString = re.sub("\n", "\n\n", infoString)
        return infoString

    def info(self):
        print(self._info())

    def infoFile(self):
        with open("README.md", "w") as file:
            file.write(self._info())

    def parseCommand(self, command):
        cmdRaw = command
        command = command
        split = command.split(" ")
        giirn = commands.getItemsInRoomNames(self, self.player.room)
        split[0] = split[0].lower()
        if split[0] in self.aliases:
            split[0] = self.aliases[split[0]]
        if split[0] == "quit":
            self.alive = False

        elif split[0] == "help":
            self.help()

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

        elif split[0] == "info":
            self.info()

        elif split[0] == "infogen":
            self.infoFile()
            print("Generated README.md file.")

        elif split[0] in self.commands:
            self = self.commands[split[0]](self, split)

        elif len(split) > 1:
            try:
                if split[1] in giirn:
                    if split[0] in self.items[giirn[split[1]]].__dict__:
                        self = self.items[giirn[split[1]]].__dict__[split[0]](self, split)
                        print("Done.")
                    else:
                        print(f"You can't {split[0]} this.")
                else:
                    print('Invalid command. Use "help" for help.')
            except:
                print(f"You can't {split[0]} this.")

        else:
            print('Invalid command. Use "help" for help.')

    def start(self):
        print(self.intro)
        lastRoom = -1
        while self.alive:
            if self.player.room != lastRoom:
                commands.look(["look"], self)
                lastRoom = self.player.room
            command = input(self.prompt)
            self.parseCommand(command)
        print(self.ending)


# pylint: disable=C0103
