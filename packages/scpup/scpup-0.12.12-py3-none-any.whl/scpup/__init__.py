"""scpup package contains the classes, constants, types, etc., needed in the
game SCPUP (Super Crystal Pokebros Ultimate Party) and any other AramEau game.
"""

import pygame
from .services import *  # noqa
from .loader import *  # noqa
from .sprite import *  # noqa
from .group import *  # noqa
from .view import *  # noqa
from .player import *  # noqa
from .ctrl import *  # noqa
from .text import *  # noqa
from .position import *  # noqa

__name__ = "scpup"
__package__ = "scpup"


def init():
  pygame.init()
