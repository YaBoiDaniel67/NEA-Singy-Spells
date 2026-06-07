import pygame
import numpy as np

screenX, screenY = 320, 180 #initial window size
display = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)
player_rotation = 0 #players rotation
xPos, yPos = (3, 3) #players coords
horizontal_res = 100 #horizontal resolution
vertical_res = 200 #vertical resolution
halfvertical_res = int(vertical_res / 2) #half the vertical resolution
scale_factor = horizontal_res/60 #scale factor - FOV is 60deg

size = 5
world_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 1],
             [1, 1, 1, 1, 1]]