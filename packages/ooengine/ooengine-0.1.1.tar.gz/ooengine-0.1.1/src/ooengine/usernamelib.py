try:
    from main import *
except:
    from .main import *


def atusername(self, split):
    if len(split) != 2:
        print("Usage: @username [username]")
        return self
    self.player.name = split[1]
    return self


def emote(self, split):
    if len(split) < 2:
        print("Usage: emote [kicks you in the shins.]")
        return self
    print(f"{self.player.name} {' '.join(split[1:])}")
    return self


def say(self, split):
    if len(split) < 2:
        print("Usage: say [Hey stinky!]")
        return self
    print(f"{self.player.name}: {' '.join(split[1:])}")
    return self


def loadMod(self):
    self.MODS.append("UsernameLib")
    self.MOD_VERSIONS.append("v1.0.0")
    self.MOD_HELPS.append(
        """### UsernameLib Help
Command list:
@username [username]
emote
say [tosay]
        """
    )
    self.commands["@username"] = atusername
    self.commands["emote"] = emote
    self.commands["say"] = say
    return self
