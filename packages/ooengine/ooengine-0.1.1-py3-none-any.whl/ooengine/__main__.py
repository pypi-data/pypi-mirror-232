## Start Imports
try:
    from main import *
    import usernamelib
except:
    from .main import *
    from . import usernamelib

## End Imports

## Start Game
game = Game()
## End Game

## Start Rooms
game.rooms.append(
    Room(
        [0],
        "You are in an empty room. There is a door to the north.",
        "Empty Room",
        {"n": 1},
        {"door": "The door is made out of white rock, with a obisidan door handle."},
    )
)
game.rooms.append(
    Room(
        [],
        "You are in another empty room. There is a door to the south.",
        "Empty Room",
        {"s": 0},
    )
)
## End Rooms

## Start Items
game.items.append(
    Item(
        "A small ball", "There is a ball here.", ["ball"], "A small red ball lies here."
    )
)
game.items[0].messages["take"] = '"Thanks for picking me up!", the ball says.'


def __item_smack(self, split):
    print('"No smacking!" the ball says.')
    return self


game.items[0].smack = __item_smack
# Item commands: set command name as command of item.
# game.items[0].smack = __item_smack
## End Items

## Custom Commands
game = usernamelib.loadMod(game)
## End Custom Commands

## Start Game
game.start()
# pylint: disable=C0103
