"""This module contains base group classes used in SCPUP

The exported classes of this module are:

* EauGroup
* EauNamedGroup
"""

from __future__ import annotations
from typing import Any, Iterator
import pygame
import scpup

__all__: list[str] = [
  "EauGroup",
  "EauNamedGroup"
]


class EauGroup:
  """A sprite group

  This sprite group class is the base clase for all the other group classes.
  This class is basically a copy of the pygame.sprite.Group class with
  __slots__ added for optimization and spritedict changed to __s, but it has a
  property called spritedict so that its compatible with pygame's groups

  Attributes:
    __s:
      Private attribute that stores the sprites that belong to this group
    lostsprites:
      Private attribute that is used to clear correctly the screen after
      removing sprites from this group
  """
  _spritegroup = True

  __slots__: tuple = (
    "__s",
    "lostsprites"
  )

  def __init__(self, *sprites: scpup.EauSprite) -> None:
    """Initializes a sprite group.

    Args:
      *sprites:
        Optionally the constructor can recieve any number of sprites that belong
        to it (To add them to this group)
    """
    self.__s: dict[scpup.EauSprite, Any] = {}
    self.lostsprites = []
    self.add(*sprites)

  def __bool__(self) -> bool:
    """Tests whether this group is empty or not

    Returns:
      bool:
        True if is not empty, False otherwise
    """
    return len(self) > 0

  def __len__(self) -> int:
    """Get the amount of sprites in this group

    Returns:
      int:
        The number of sprites that belong to this group
    """
    return len(self.__s)

  def __iter__(self) -> Iterator:
    """Returns an iterator of the sprites in this group"""
    return iter(self.sprites())

  def __contains__(self, sprite: scpup.EauSprite) -> bool:
    """Tests whether a sprite exists or not in this group

    Args:
      sprite:
        The sprite to test if belongs or not

    Returns:
      bool:
        True if the sprite belongs to this group, False otherwise
    """
    return sprite in self.__s

  def __getitem__(self, idx: int) -> scpup.EauSprite:
    """Get a sprite by index.

    I haven't tested if this method affects the performance but I think that it
    is not the best method to use.

    Args:
      idx:
        The index of the sprite.

    Raises:
      IndexError:
        Index out of range.

    Returns:
      scpup.EauSprite:
        The found sprite.
    """
    if 0 < self.__len__() < idx:
      return self.sprites()[idx]
    raise IndexError('Index out of range')

  @property
  def spritedict(self) -> dict[scpup.EauSprite, Any]:
    """Get the self.__s attribute. Basically this is just for compatibility
    issues with pygame.sprite.Group and its subclasses

    Returns:
      dict:
        The attribute __s
    """
    return self.__s

  def add_internal(self, sprite: scpup.EauSprite) -> None:
    """Private method used to register a sprite that belongs to this group

    Args:
      sprite: The sprite to register
    """
    self.__s[sprite] = 0

  def remove_internal(self, sprite: scpup.EauSprite) -> None:
    """Private method used to remove a registered sprite

    Args:
      sprite: The sprite to remove
    """
    lost_rect = self.__s[sprite]
    if lost_rect:
      self.lostsprites.append(lost_rect)
    del self.__s[sprite]

  def sprites(self) -> list[scpup.EauSprite]:
    """Get a list of the sprites in this group

    TODO: Maybethis should be a property...

    Returns:
      list:
        A list of the sprites that belong to this group
    """
    return list(self.__s)

  def add(self, *sprites: scpup.EauSprite) -> None:
    """Add sprites to this group

    Args:
      *sprites:
        The sprites to be added. These can be either pygame.srite.Sprite or
        scpup.EauSprite or any subclass of these.
    """
    for sprite in sprites:
      if sprite not in self.__s:
        self.add_internal(sprite)
        sprite.add_internal(self)

  def remove(self, *sprites: scpup.EauSprite) -> None:
    """Remove sprites from this group

    Args:
      *sprites:
        The sprites to be removed. These can be either pygame.srite.Sprite or
        scpup.EauSprite or any subclass of these
    """
    for sprite in sprites:
      if sprite in self.__s:
        self.remove_internal(sprite)
        sprite.remove_internal(self)

  def update(self, *args, **kwargs) -> None:
    """Call the update method of the sprites in this group"""
    for sprite in self.sprites():
      sprite.update(*args, **kwargs)

  def draw(self, surface: pygame.Surface) -> None:
    """Draws the sprites that belong to this group on a given surface

    Args:
      surface:
        The pygame.Surface to draw the sprites to
    """
    sprites: list[scpup.EauSprite] = self.sprites()
    self.draw_internal(surface, sprites)

  def draw_internal(self, surface: pygame.Surface, sprites: list[scpup.EauSprite]) -> None:
    """Private method used to draw the sprites to a surface

    This method is used by the draw method but exists so that subclasses can
    decide which sprites should be drawn if for any reason not all sprites need
    to be drawn

    Args:
        surface:
          The pygame.Surface to draw the sprites to
        sprites:
          The sprites to draw to the surface
    """
    if hasattr(surface, "blits"):
      self.__s.update(
        zip(
          sprites,
          surface.blits(
            (spr.image, spr.rect, None) for spr in sprites
          )  # type: ignore
        )
      )
    else:
      for spr in sprites:
        if spr.image is not None and spr.rect is not None:
          self.__s[spr] = surface.blit(spr.image, spr.rect, None)
    self.lostsprites = []

  def clear(self, surface: pygame.Surface, bg: pygame.Surface) -> None:
    """Clear the sprites that were last drawn from a surface using a background

    Args:
      surface:
        The pygame.Surface to clear the sprites from
      bg:
        The pygame.Surface that will be used to clear the sprites from the
        surface
    """
    for lost_clear_rect in self.lostsprites:
      surface.blit(bg, lost_clear_rect, lost_clear_rect)
    for clear_rect in self.__s.values():
      if clear_rect:
        surface.blit(bg, clear_rect, clear_rect)

  def empty(self) -> None:
    """Remove all sprites from this group. THIS STILL HAS THE FUNCTIONALITY IT
    HAD BEFORE COMMENTED OUT BECAUSE IT HAS NOT BEEN TESTED"""
    self.remove(*self.sprites())
    # for sprite in self.__s:
    #   self.remove_internal(sprite)
    #   sprite.remove_internal(self)


class EauNamedGroup(EauGroup):
  """A group with named subgroups for a better organization

  Attributes:
    __n:
      Private attribute that stores the subgroups names along with the sprites
      that each group contains. All named groups have an 'all' group for sprites
      that don't belong to a specific subgroup.
  """
  __slots___: tuple = (
    "__n",
  )

  def __init__(self, *sprites: scpup.EauSprite, name: str = 'all') -> None:
    """Initializes a named group. Optionally sprites can by added to a subgroup
    when initializing the group

    Args:
      *sprites:
        The sprites that will be added to the subgroup
      name:
        The name of the subgroup, by default its 'all'
    """
    super().__init__(*sprites)
    self.__n: dict[str, list[scpup.EauSprite]] = {'all': []}
    self.__n[name] = list(sprites)

  def group(self, name: str) -> list[scpup.EauSprite]:
    """Get a list of the sprites in a subgroup

    Args:
      name:
        The name of the subgroup

    Returns:
      list:
        A list of sprites found, or an empty list if the subgroup does not exist
        in this group
    """
    if name in self.__n:
      return self.__n[name]
    return []

  def add(self, *sprites: scpup.EauSprite, name: str = 'all') -> None:
    """Add sprites to a subgroup of this group

    Args:
      *sprites:
        The sprites to be added
      name:
        The name of the subgroup. 'all' by default
    """
    super().add(*sprites)
    if name != 'all':
      for s in sprites:
        self.transfer(s, name)

  def add_internal(self, sprite: scpup.EauSprite) -> None:
    super().add_internal(sprite)
    self.__n['all'].append(sprite)

  def remove_internal(self, sprite: scpup.EauSprite) -> None:
    super().remove_internal(sprite)
    sprites_list = next(filter(lambda s: sprite in s, self.__n.values()), None)
    if sprites_list:
      sprites_list.remove(sprite)

  def empty(self, name: str | None = None) -> None:
    """Remove all sprites from a subgroup of this group

    Args:
      name:
        The name of the subgroup to empty. If None is passed then empty the
        whole group
    """
    self.remove(*self.sprites(name))
    if name is None:
      self.__n.clear()
    else:
      self.__n[name] = []

  def sprites(self, name: str | None = None) -> list[scpup.EauSprite]:
    """Get a list of the sprites in a subgroup of this group

    Args:
      name:
        The name of the subgroup to search. If None is passed then get the
        sprites of the whole group

    Returns:
      list:
        A list of sprites
    """
    return super().sprites() if name is None else self.__n[name] if name in self.__n else []

  def update(self, *args, name: str | None = None, **kwargs) -> None:
    """Call the update method of the sprites in a subgroup of this group

    Example calls of this method:

    ```python
    named_group.update(name='subgroup_name')
    named_group.update('value', name='subgroup_name')
    named_group.update(name='subgroup_name', kwarg='value')
    named_group.update('value', name='subgroup_name', kwarg='value')
    ```

    Args:
      name:
        The name of the subgroup to update. If None is passed then update the
        whole group
    """
    for sprite in self.sprites(name):
      sprite.update(*args, **kwargs)

  def draw(self, surface: pygame.Surface, name: str | None = None) -> None:
    """Draws the sprites that belong to a subgroup of this group on a surface

    Args:
      name:
        The name of the subgroup to draw. If None is passed then the whole group
        is drawn
      surface:
        The pygame.Surface to draw the sprites to
    """
    sprites: list[scpup.EauSprite] = self.sprites(name)
    self.draw_internal(surface, sprites)

  def transfer(self, sprite: scpup.EauSprite | None, name: str) -> None:
    """Move a sprite from its current group to another group

    Args:
      sprite:
        The sprite to move. (Added the '| None' to the type of this parameter
        so that you can pass an object that may be a sprite or None to this
        function but if None is passed it doesn't do anything)
      name:
        The name of the group to move the sprite to. If the group does not exist
        yet it will be created.
    """
    if sprite is None:
      return
    sprites_list = next(filter(lambda s: sprite in s, self.__n.values()), None)
    if sprites_list:
      sprites_list.remove(sprite)
      if name in self.__n:
        self.__n[name].append(sprite)
      else:
        self.__n[name] = [sprite]
