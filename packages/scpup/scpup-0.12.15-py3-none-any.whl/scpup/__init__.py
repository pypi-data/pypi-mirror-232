"""scpup package contains the classes, constants, types, etc., needed in the
game SCPUP (Super Crystal Pokebros Ultimate Party) and any other AramEau game.
"""

import pygame
from .services import EauService  # noqa
from .text import *  # noqa
from .loader import *  # noqa
from .sprite import *  # noqa
from .group import *  # noqa
from .view import *  # noqa
from .player import *  # noqa
from .ctrl import *  # noqa
from .position import *  # noqa

__name__ = "scpup"
__package__ = "scpup"


def init(window_attrs: dict):
  from .services import EauDisplayService, EauEventService
  from .text import EauText
  pygame.init()
  EauDisplayService.set_window_attrs(**window_attrs)
  EauDisplayService()
  EauEventService()
  if not EauText._fontpath_:
    raise RuntimeError('Font path has not been set!!!')
