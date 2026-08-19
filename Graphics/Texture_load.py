import pygame
from pygame.locals import *
import Variables as var
display = var.display

sky = pygame.image.load("Graphics/Textures/sky.png").convert()
sky = pygame.surfarray.array3d(pygame.transform.scale(sky, (360, var.vertical_res)))

floor = pygame.image.load("Graphics/Textures/Floor.png").convert()
floor = pygame.surfarray.array3d(pygame.transform.scale(floor, (100, var.halfvertical_res )))

wall = pygame.image.load("Graphics/Textures/Wall.png").convert()
wall = pygame.surfarray.array3d(pygame.transform.scale(wall, (100, var.halfvertical_res)))

Fireball = pygame.image.load("Graphics/Textures/Fireball.png").convert()
Fireball = pygame.surfarray.array3d(Fireball)
#converts the textures into scaled images, and then surfarray.3darray converts the image into a 3d numpy array of dimensions width, height, and a list of the pixels 3 RGB values