import os
import pygame
import pygame.mixer
import pygame.freetype

__all__ = [
  "load_image",
  "load_sound",
  "BASE_PATH"
]

BASE_PATH = os.path.join(os.getcwd(), "assets")


def load_image(*paths: str, alpha=True, **rectargs) -> tuple[pygame.Surface, pygame.Rect]:
  """Loads an image located somewhere in <root>/assets/images/...

  Args:
    *paths:
      The path segments of where the image file exists.
    alpha:
      Whether the image should convert pixel format considering transparency or
      not. Defaults to True.
    **rectargs:
      Any arguments to pass to the image.get_rect() method. Basically to set an
      initial position.

  Raises:
    ValueError:
      The given image path does not exist.

  Returns:
    tuple[pygame.Surface, pygame.Rect]:
      The image as a pygame.Surface and the covering rectangle of that image.
  """
  path = os.path.join(BASE_PATH, "images", *paths)
  if not os.path.exists(path):
    raise ValueError(f"Path: '{path}' does not exist")
  image = pygame.image.load(path)
  if alpha:
    image = image.convert_alpha()
  else:
    image = image.convert()
  rect = image.get_rect(**rectargs)
  return image, rect


def load_sound(*paths: str) -> pygame.mixer.Sound:
  """Loads a sound file located somewhere in <root>/assets/sounds...

  Args:
    *paths:
      The path segments of where the sound file exists

  Returns:
    pygame.mixer.Sound:
      The loaded sound.
  """
  path: str = os.path.join(BASE_PATH, "sounds", *paths)
  sound = pygame.mixer.Sound(path)
  return sound
