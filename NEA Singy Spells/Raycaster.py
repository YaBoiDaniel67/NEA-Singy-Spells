import numpy as np
import pygame

rot_r = 0

environment = [[0, 0, 1, 1, 1],
               [0, 0, 0, 0, 1],
               [1, 0, 1, 0, 1],
               [1, 0, 0, 0, 1],
               [1, 1, 1, 1, 1]]

def RayCast(display, fov, xPos, yPos):
  for i in range(fov):
    rot_d = rot_r + np.radians(i - fov/2)
    x, y = (xPos, yPos)
    sin, cos = (0.02*np.sin(rot_d), 0.02*np.cos(rot_d))
    j = 0
    while True:
      x, y = (x + cos, y + sin)
      j += 1
      if environment[int(x) % 5][int(y) % 5] != 0:
        height = (10/j * 2500)
        break
    pygame.draw.line(display, (255 % height, 255 % height, 255 % height), (i*(1600/fov), 900/2+height), (i*(1600/fov), 900/2-height), width=int(1600/fov))