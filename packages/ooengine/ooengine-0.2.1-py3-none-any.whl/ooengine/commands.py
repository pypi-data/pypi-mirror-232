"""Basic commands for OOEngine."""


class NoBallsError(Exception):
    """A sample error for no balls (used for checking if there is a ball in the room)."""


def get_items_in_room(self, room):
    """Get all items in the room given as a array of objects."""
    try:
        items = self.rooms[room].items
        new_items = []
        for item in items:
            new_items.append(self.items[item].__dict__)
        return new_items
    except IndexError:
        return []


def get_items_in_room_names(self, room):
    """Get the short names of all items in a room."""
    try:
        items = self.rooms[room].items
        new_items = {}
        for item in items:
            new_items[self.items[item].short[0]] = item
        return new_items
    except IndexError:
        return []


def get_items_in_inventory_names(self, room):
    """Get the short names of all items in the inventory."""
    items = room
    try:
        new_items = {}
        for item in items:
            new_items[self.items[item].short[0]] = item
        return new_items
    except IndexError:
        return []


def look(split, self):
    """Look at objects in the room. Called from main.py."""
    try:
        if len(split) == 1:
            print(self.rooms[self.player.room].description)
            for item in self.rooms[self.player.room].items:
                print(self.items[item].on_floor)
        elif len(split) > 1:
            giirn = get_items_in_room_names(self, self.player.room)
            split[1] = ' '.join(split[1:])
            if split[1] in giirn:
                print(self.items[giirn[split[1]]].long)
            else:
                print(self.rooms[self.player.room].looks[split[1]])
        else:
            print("Usage: look [where]")
    except (IndexError, KeyError):
        print("You can't look at that.")


def grab(split, self):
    """Grab an item in the room. Called from main.py."""
    try:
        if len(split) == 2:
            giirn = get_items_in_room_names(self, self.player.room)
            if split[1] in giirn:
                self.player.inventory.append(giirn[split[1]])
                self.rooms[self.player.room].items.remove(giirn[split[1]])
                self.items[self.player.inventory[-1]].take()
                print("Okay.")
            else:
                print("You can't take that.")
        else:
            print("Usage: take [item]")
    except IndexError:
        print("You can't take that.")
    return self


def drop(split, self):
    """Drop an item in inventory. Called from main.py."""
    try:
        if len(split) == 2:
            giirn = get_items_in_inventory_names(self, self.player.inventory)
            if split[1] in giirn:
                self.player.inventory.remove(giirn[split[1]])
                self.rooms[self.player.room].items.append(giirn[split[1]])
                self.items[self.rooms[self.player.room].items[-1]].drop()
                print("Okay.")
            else:
                print("You can't drop that.")
        else:
            print("Usage: drop [item]")
    except IndexError:
        print("You can't drop that.")
    return self


def eat(split, self):
    """Eat an item in your inventory. Called from main.py."""
    try:
        if len(split) == 2:
            giirn = get_items_in_inventory_names(self, self.player.inventory)
            if split[1] in giirn and (
                self.items[giirn[split[1]]].messages["eat"] is not None
            ):
                self.items[self.player.inventory[-1]].eat()
                self.player.inventory.remove(giirn[split[1]])
                print("Okay.")
            else:
                print("You can't eat that.")
        else:
            print("Usage: eat [item]")
    except (IndexError, KeyError):
        print("You can't eat that.")
    return self


def unlock(self, split):
    """Unlock a door in a room. Called from main.py."""
    try:
        current_room = self.rooms[self.player.room]
        if len(split) == 1:
            if current_room.locked is not {}:
                if current_room.key in self.player.inventory:
                    self.rooms[self.player.room].exits.update(current_room.locked)
                    self.rooms[
                        self.player.room
                    ].description = current_room.unlocked_desc
                    print("You unlocked the door!")
                else:
                    print("You don't have the key!")
            else:
                print("What am I supposed to be unlocking here?")
        else:
            print("Usage: unlock")
    except IndexError:
        print("You can't unlock that.")
    return self


def inventory(self, split):
    """Print the player's inventory. Called from main.py."""
    if split is None:
        raise NoBallsError
    print("You have:")
    if len(self.player.inventory) == 0:
        print("Nothing!")
    for item in self.player.inventory:
        print(self.items[item].name)


# pylint: disable=C0103
