"""scpup package contains the classes, constants, types, etc., needed in the
game SCPUP (Super Crystal Pokebros Ultimate Party) and any other AramEau game.
"""

from __future__ import annotations
from typing import TypedDict

import pygame

from .services import EauService, EAU_EVENT  # noqa
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


class WindowAttrs(TypedDict):
    size: tuple[int, int] | None
    caption: str | None
    icon_path: str | None


def init(window_attrs: WindowAttrs):
  from .services import EauDisplayService, EauEventService
  from .text import EauText
  if not EauText._fontpath_:
    raise RuntimeError('Font path has not been set.')
  pygame.init()
  EauDisplayService(
    size=window_attrs['size'] or (1200, 800),
    caption=window_attrs['caption'],
    icon_path=window_attrs['icon_path']
  )
  EauEventService()
