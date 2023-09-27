class NoBallsError(Exception):
    pass


def getItemsInRoom(self, room):
    items = self.rooms[room].items
    newItems = []
    for item in items:
        newItems.append(self.items[item].__dict__)
    return newItems


def getItemsInRoomNames(self, room):
    items = self.rooms[room].items
    newItems = {}
    for item in items:
        newItems[self.items[item].short[0]] = item
    return newItems


def getItemsInInventNames(self, room):
    items = room
    newItems = {}
    for item in items:
        newItems[self.items[item].short[0]] = item
    return newItems


def look(split, self):
    try:
        if len(split) == 1:
            print(self.rooms[self.player.room].description)
            for item in self.rooms[self.player.room].items:
                print(self.items[item].onFloor)
        elif len(split) == 2:
            giirn = getItemsInRoomNames(self, self.player.room)
            if split[1] in giirn.keys():
                print(self.items[giirn[split[1]]].long)
            else:
                print(self.rooms[self.player.room].looks[split[1]])
        else:
            print("Usage: look [where]")
    except:
        print("You can't look at that.")


def grab(split, self):
    try:
        if len(split) == 2:
            giirn = getItemsInRoomNames(self, self.player.room)
            if split[1] in giirn.keys():
                self.player.inventory.append(giirn[split[1]])
                self.rooms[self.player.room].items.remove(giirn[split[1]])
                self.items[self.player.inventory[giirn[split[1]]]].take()
                print("Okay.")
            else:
                print("You can't take that.")
        else:
            print("Usage: take [item]")
    except:
        print("You can't take that.")
    return self


def drop(split, self):
    try:
        if len(split) == 2:
            giirn = getItemsInInventNames(self, self.player.inventory)
            if split[1] in giirn.keys():
                self.player.inventory.remove(giirn[split[1]])
                self.rooms[self.player.room].items.append(giirn[split[1]])
                self.items[self.rooms[self.player.room].items[giirn[split[1]]]].drop()
                print("Okay.")
            else:
                print("You can't drop that.")
        else:
            print("Usage: drop [item]")
    except:
        print("You can't drop that.")
    return self


def eat(split, self):
    try:
        if len(split) == 2:
            giirn = getItemsInInventNames(self, self.player.inventory)
            if (
                split[1] in giirn.keys()
                and self.items[giirn[split[1]]].messages["eat"] != None
            ):
                self.items[self.player.inventory[giirn[split[1]]]].eat()
                self.player.inventory.remove(giirn[split[1]])
                print("Okay.")
            else:
                print("You can't eat that.")
        else:
            print("Usage: eat [item]")
    except:
        print("You can't eat that.")
    return self


def inventory(self, split):
    print("You have:")
    if len(self.player.inventory) == 0:
        print("Nothing!")
    for item in self.player.inventory:
        print(self.items[item].name)


# pylint: disable=C0103
