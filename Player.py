import pygame
import numpy as np

def Movement(xPos, yPos, world_map, player_rotation, keys, humming):
    x, y = xPos, yPos
    if keys[ord('a')]: #is key at index ord('a') currently being held down
        player_rotation -= 0.05
    if keys[ord('d')]: #is key at index ord('d') currently being held down 
        player_rotation += 0.05
    if keys[ord('w')] or humming == True: #is key at index ord('w') currently being held down
        x, y = x + np.cos(player_rotation) * 0.05, y + np.sin(player_rotation) * 0.05
    if keys[ord('s')]: #is key at index ord('s') currently being held down
        x, y = x - np.cos(player_rotation) * 0.05, y - np.sin(player_rotation) * 0.05
    if not (world_map[int(x - 0.1)][int(y)] or world_map[int(x + 0.1)][int(y)] or world_map[int(x)][int(y - 0.1)] or world_map[int(x)][int(y + 0.1)]): #if the player is not about to move into a wall, their position updates
        xPos, yPos = x, y
    elif not (world_map[int(xPos - 0.1)][int(y)] or world_map[int(xPos + 0.1)][int(y)] or world_map[int(xPos)][int(y - 0.1)] or world_map[int(xPos)][int(y + 0.1)]): #if the x is about to move into a wall but the y is not, the y updates
        yPos = y
    elif not (world_map[int(x - 0.1)][int(yPos)] or world_map[int(x + 0.1)][int(yPos)] or world_map[int(x)][int(yPos - 0.1)] or world_map[int(x)][int(yPos + 0.1)]): #if the y is about to move into a wall but the x is not, the x updates
        xPos = x
    return xPos, yPos, player_rotation
#checks whether the player has moved, and adjusts value acoordingly so they move in game space