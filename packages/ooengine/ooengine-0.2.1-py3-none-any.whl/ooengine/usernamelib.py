"""A set of username-related commands (for MUDs.)"""
try:
    from main import RANDOM
except ImportError:
    from .main import RANDOM

RANDOM = RANDOM + 1


def atusername(self, split):
    """@username: Set username of player."""
    if len(split) != 2:
        print("Usage: @username [username]")
        return self
    self.player.name = split[1]
    return self


def emote(self, split):
    """emote: Roleplaying at its finest."""
    if len(split) < 2:
        print("Usage: emote [kicks you in the shins.]")
        return self
    print(f"{self.player.name} {' '.join(split[1:])}")
    return self


def say(self, split):
    """Say stuff to other players. If there are any."""
    if len(split) < 2:
        print("Usage: say [Hey stinky!]")
        return self
    print(f"{self.player.name}: {' '.join(split[1:])}")
    return self


def load_mod(self):
    """Load myself."""
    self.mods.append("UsernameLib")
    self.mod_versions.append("v1.0.0")
    self.mod_helps.append(
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
