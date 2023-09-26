from __future__ import annotations

import pygame
import scpup
from typing import Any, Literal, final, overload


__all__: list[str] = [
  "EauService",
  "EauDisplayService",
  "EauEventService"
]

# TODO: Maybe change eaudisplayservice.__init__ so it doesn't receive params
#       and instead the current params are set in a classmethod or something,
#       So I can remove the get classmethod in the eau service class


class EauServiceMeta(type):
  _instances_: dict[str, Any] = {}

  def __call__(cls, *args, **kwds) -> Any:
    if cls.__name__ not in cls._instances_:
      instance = super().__call__(*args, **kwds)
      cls._instances_[cls.__name__] = instance
    return cls._instances_[cls.__name__]


class EauService(metaclass=EauServiceMeta):
  @overload
  @classmethod
  def get(cls, service_name: Literal['EauDisplayService']) -> EauDisplayService | None:
    """Get the display service or None if it has not been created yet"""
  @overload
  @classmethod
  def get(cls, service_name: Literal['EauEventService']) -> EauEventService | None:
    """Get the event service or None if it has not been created yet"""
  @classmethod
  def get(cls, service_name: str) -> EauService | None:
    return cls._instances_.get(service_name, None)


@final
class EauDisplayService(EauService):
  """A service used for all display related tasks

  Attributes:
    _display:
      The main display of the game
    _background:
      The background of the current view
    _default_bg:
      The default background used in views that don't have a background
    _view:
      The current view that is being rendered
    viewport:
      The main display rect
  """

  __slots__: tuple = (
    "_display",
    "_background",
    "_view",
    "_default_bg",
    "viewport"
  )

  def __init__(self, icon_path: str, caption: str, size: tuple[int, int] | None = None):
    """Initialize the display service, optionally with a display size

    Args:
      icon_path:
        Path of the image if the icon of the game window
      caption:
        The caption of the game window
      size:
        The display size. If omitted the display size will be set to 1200*800
        (which is the size of the display for scpup)
    """
    if size:
      self.viewport = pygame.Rect(0, 0, *size)
    else:
      self.viewport = pygame.Rect(0, 0, 1200, 800)
    self._display: pygame.Surface = pygame.display.set_mode(self.size)
    img, _ = scpup.load_image(icon_path)
    pygame.display.set_icon(img)
    pygame.display.set_caption(caption)
    pygame.mouse.set_visible(0)
    self.viewport.size = self._display.get_size()
    self._view: scpup.EauView | None = None
    bg = pygame.Surface(self.size)
    bg.fill(pygame.Color(86, 193, 219))
    self._default_bg = bg.convert()
    self._background: pygame.surface.Surface = self._default_bg

  @property
  def size(self) -> tuple[int, int]:
    """Get the size of the viewport rectangle"""
    return self.viewport.size

  @property
  def view(self) -> scpup.EauView | None:
    """Get the current view"""
    return self._view

  @view.setter
  def view(self, view: scpup.EauView) -> None:
    """Set the current view

    If there was a view already being rendered, this method first clears the
    display and then sets the view. It also sets the players sprites
    """
    if self.view:
      self.view.sprites.clear(self._display, self._background)
    self._view = view
    self._background = view.background or self._default_bg
    self._display.blit(self._background, (0, 0))
    scpup.EauPlayer.set_sprites(view.player_sprite)

  def update_view(self, *args, **kwargs) -> None:
    """Main display update method

    This method calls the `clear` method, then the `update` method, and then the
    `draw` method of the view and the players. This method also checks for
    collitions between the players sprites and the view sprites, and then
    between the players sprites and the other players sprites.

    Args:
      *args, **kwargs:
        Any arguments to pass to the sprites update method
    """
    if self.view:
      self.view.clear(self._display, self._background)
      scpup.EauPlayer.clear(self._display, self._background)
      self.view.update(*args, rect=self.viewport, **kwargs)
      scpup.EauPlayer.update(*args, rect=self.viewport, **kwargs)
      self.view.draw(self._display)
      scpup.EauPlayer.draw(self._display)
      scpup.EauPlayer.check_collitions(self.view.sprites)
    pygame.display.flip()


@final
class EauEventService(EauService):
  """A service used for event related tasks"""
  __slots__ = ()

  def __init__(self) -> None:
    pygame.key.set_repeat()
    pygame.key.stop_text_input()
    pygame.event.set_blocked([
        pygame.MOUSEMOTION,
        pygame.WINDOWLEAVE,
        pygame.WINDOWENTER,
        pygame.WINDOWFOCUSLOST,
        pygame.WINDOWFOCUSGAINED,
        pygame.WINDOWSHOWN,
        pygame.WINDOWCLOSE,
        pygame.ACTIVEEVENT,
        pygame.MOUSEBUTTONDOWN,
        pygame.MOUSEBUTTONUP,
        pygame.VIDEOEXPOSE,
        pygame.VIDEORESIZE,
        pygame.WINDOWEXPOSED,
        pygame.AUDIODEVICEADDED,
        pygame.AUDIODEVICEREMOVED
    ])
    # pygame.event.clear()

  def handle_event(self, event):
    """Main event handler

    This method handles an event. It is intended to be so generic that it can be
    used in scpup as well as in other games, but work still in progress....

    Args:
      event:
        The pygame.event.Event to handle.
    """
    if event.type == pygame.JOYDEVICEADDED:
      j: pygame.joystick.Joystick = pygame.joystick.Joystick(event.device_index)
      scpup.EauCtrl(j)

    elif event.type == pygame.JOYDEVICEREMOVED:
      scpup.EauPlayer.remove_player(event.instance_id)
      scpup.EauCtrl.remove_ctrl(event.instance_id)

    elif event.type in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN]:
      player: scpup.EauPlayer | None = scpup.EauPlayer(event.instance_id)
      if player:
        if event.type == pygame.JOYAXISMOTION:
          player.handle_joystick_input(event.axis, event.value)
        else:
          player.handle_joystick_input(event.button)
      elif event.type == pygame.JOYBUTTONDOWN:
        ctrl = scpup.EauCtrl(event.instance_id)
        if ctrl.action(event.button) == scpup.EauAction.START:
          try:
            new_player: scpup.EauPlayer = next(scpup.EauPlayer)
            new_player.assign_ctrl(ctrl)
          except StopIteration:
            return
