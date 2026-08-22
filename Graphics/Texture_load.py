import pygame
from pygame.locals import *

def load_textures(half_vertical_res):
  texture_list = {}

  play_button = pygame.image.load("Graphics/Textures/Play_Button.png").convert()
  texture_list.update({"play_button" : play_button})

  sky = pygame.image.load("Graphics/Textures/sky.png").convert()
  sky = pygame.surfarray.array3d(sky)
  texture_list.update({"sky" : sky})

  floor = pygame.image.load("Graphics/Textures/Floor.png").convert()
  floor = pygame.surfarray.array3d(pygame.transform.scale(floor, (100, half_vertical_res )))
  texture_list.update({"floor": floor})

  wall = pygame.image.load("Graphics/Textures/Wall.png").convert()
  wall = pygame.surfarray.array3d(pygame.transform.scale(wall, (100, half_vertical_res)))
  texture_list.update({"wall" : wall})

  Fireball = pygame.image.load("Graphics/Textures/Fireball.png").convert()
  Fireball = pygame.surfarray.array3d(Fireball)
  texture_list.update({"Fireball" : Fireball})

  Star = pygame.image.load("Graphics/Textures/Star.png").convert()
  Star = pygame.surfarray.array3d(Star)
  texture_list.update({"Star" : Star})

  return texture_list

#converts the textures into scaled images, and then surfarray.3darray converts the image into a 3d numpy array of dimensions width, height, and a list of the pixels 3 RGB values