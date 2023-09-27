
from .config import DESTRUCTIVE_COMMANDS

def is_destructive(command):
    """Checks if a Docker command is potentially destructive based on predefined configurations."""
    for destructive_command, explanation in DESTRUCTIVE_COMMANDS.items():
        if destructive_command in command:
            return True, explanation
    return False, "non destructive."

