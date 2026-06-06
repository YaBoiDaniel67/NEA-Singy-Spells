import pygame
from pygame.locals import *
import numpy as np
import Raycaster as Raycast
import Player as player
import Variables as var
#imports all librarys needed for this project

display = var.display
player_rotation = var.player_roatation
xPos, yPos = var.xPos, var.yPos
hres = var.horizontal_res
halfvres = var.halfvertical_res
scale_factor = var.scale_factor
clock = pygame.time.Clock()
frame = np.random.uniform(0,1, (hres, halfvres*2, 3))
#sets up initial variables, many pulling form my varaibles file, which is where variables accsssed by many files are initialised

run = True
while run: #creates an indefinite loop to keep the game running
    display.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False #if the cross button is pressed, the window closes - allows exit of the program
    Raycast.RayCast(display, xPos, yPos, frame, hres, halfvres, scale_factor, player_rotation, var.world_map) #calls the raycast subroutine
    xPos, yPos, player_rotation = player.Movement(xPos, yPos, player_rotation, pygame.key.get_pressed()) #calls the movement subroutine
    pygame.display.update() #updates the display
    var.screenX, var.screenY = display.get_size() #updates screen size, so that game scales to size of screen