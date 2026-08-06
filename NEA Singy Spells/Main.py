import pygame
from pygame.locals import *
import numpy as np
import Raycaster as Raycast

fov = 80
xPos, yPos = (1, 1)

display = pygame.display.set_mode((1600, 900))
run = True
while run:
    display.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            while event.key == K_a:
                Raycast.rot_r = (Raycast.rot_r - 0.1) % (np.pi * 2)
            if event.key == K_d:
                Raycast.rot_r = (Raycast.rot_r + 0.1) % (np.pi * 2)
            if event.key == K_w:
                xPos += 0.2 * np.cos(Raycast.rot_r)
                yPos += 0.2 * np.sin(Raycast.rot_r)
            if event.key == K_s:
                xPos -= 0.2 * np.cos(Raycast.rot_r)
                yPos -= 0.2 * np.sin(Raycast.rot_r)
    Raycast.RayCast(display, fov, xPos, yPos)
    pygame.display.update()