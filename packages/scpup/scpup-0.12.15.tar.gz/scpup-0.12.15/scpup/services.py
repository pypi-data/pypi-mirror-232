from __future__ import annotations

import pygame
import pygame.event
import scpup
from typing import Any, Literal, final, overload


__all__: list[str] = [
  "EauService",
  "EauDisplayService",
  "EauEventService",
  "EAU_EVENT"
]


EAU_EVENT = pygame.event.custom_type()


class EauServiceMeta(type):
  _instances_: dict[str, Any] = {}

  def __call__(cls, *args, **kwds) -> Any:
    if cls.__name__ not in cls._instances_:
      instance = super().__call__(*args, **kwds)
      cls._instances_[cls.__name__] = instance
    return cls._instances_[cls.__name__]


class EauService(metaclass=EauServiceMeta):
  """Base class for scpup services. If you want to use a service you'll need to
  call EauService.get and pass the service name as an argument"""
  @overload
  @classmethod
  def get(cls, service_name: Literal['EauDisplayService']) -> EauDisplayService:
    """Get the display service"""
  @overload
  @classmethod
  def get(cls, service_name: Literal['EauEventService']) -> EauEventService:
    """Get the event service"""
  @classmethod
  def get(cls, service_name: str) -> EauService:
    service = cls._instances_.get(service_name, None)
    if not service:
      raise RuntimeError(f"Service '{service_name}' does not exist or has not been initialized.")
    return service


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

  Class Attributes:
    icon_path:
      The path of the icon of the game window
    caption:
      The title of the game window
    size:
      the size of the game window in a tuple like this: (width, height). By
      default width is 1200 and height is 800.
  """
  icon_path: str | None = None
  caption: str | None = None
  size: tuple[int, int] = (1200, 800)

  __slots__: tuple = (
    "_display",
    "_background",
    "_view",
    "_default_bg",
    "viewport"
  )

  @classmethod
  def set_window_attrs(
    cls,
    icon_path: str | None = None,
    caption: str | None = None,
    size: tuple[int, int] | None = None
  ) -> None:
    """Set the attributes of the game window. Use this before initializing
    the scpup module. If the parameters are set to None they won't be taken in
    consideration, and by default they are all None.

    Args:
      icon_path:
        The path of the game window icon.
      caption:
        The game window title.
      size:
        The game window size.
    """
    if icon_path:
      cls.icon_path = icon_path
    if caption:
      cls.caption = caption
    if size:
      cls.size = size

  def __init__(self):
    """Initialize the display service"""
    self.viewport = pygame.Rect(0, 0, *self.size)
    self._display: pygame.Surface = pygame.display.set_mode(self.size)
    if self.icon_path:
      img, _ = scpup.load_image(self.icon_path)
      pygame.display.set_icon(img)
    if self.caption:
      pygame.display.set_caption(self.caption)
    pygame.mouse.set_visible(0)
    self._view: scpup.EauView | None = None
    bg = pygame.Surface(self.size)
    bg.fill(pygame.Color(86, 193, 219))
    self._default_bg = bg.convert()
    self._background: pygame.surface.Surface = self._default_bg

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
      elif event.type == EAU_EVENT:
        ...

  def send(self, event_name: str, **kwargs):
    ev = pygame.event.Event(EAU_EVENT, {
      'name': event_name,
      **kwargs
    })
    pygame.event.post(ev)
