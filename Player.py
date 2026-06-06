import pygame
from pygame.locals import *
import numpy as np
import Variables as var


def Movement(xPos, yPos, rot, keys):
    x, y = xPos, yPos
    if keys[ord('a')]:
        rot -= 0.1
    if keys[ord('d')]:
        rot += 0.1
    if keys[ord('w')]:
        x, y = x + np.cos(rot) * 0.1, y + np.sin(rot) * 0.1
    if keys[ord('s')]:
        x, y = x - np.cos(rot) * 0.1, y - np.sin(rot) * 0.1
    if not (var.world_map[int(x - 0.1)][int(y)] or var.world_map[int(x + 0.1)][int(y)] or var.world_map[int(x)][int(y - 0.1)] or var.world_map[int(x)][int(y + 0.1)]): #if the player is not about to move into a wall, their position updates
        xPos, yPos = x, y
    elif not (var.world_map[int(xPos - 0.1)][int(y)] or var.world_map[int(xPos + 0.1)][int(y)] or var.world_map[int(xPos)][int(y - 0.1)] or var.world_map[int(xPos)][int(y + 0.1)]): #if the x is about to move into a wall but the y is not, the y updates
        yPos = y
    elif not (var.world_map[int(x - 0.1)][int(yPos)] or var.world_map[int(x + 0.1)][int(yPos)] or var.world_map[int(x)][int(yPos - 0.1)] or var.world_map[int(x)][int(yPos + 0.1)]): #if the y is about to move into a wall but the x is not, the x updates
        xPos = x
    return xPos, yPos, rot
#checks whether the player has moved, and adjusts value acoordingly so they move in game space