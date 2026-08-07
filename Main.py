import pygame
from pygame.locals import *
import numpy as np
#imports all librarys needed for this file
import Raycaster as Raycast
import Player as player
import Variables as var
import Audio.Audio_Input as audio
#import the other files
pygame.font.init()
font = pygame.font.SysFont(None, int(var.screenX * 0.1))

display = var.display
clock = pygame.time.Clock()
frame = np.random.uniform(0, 1, (var.horizontal_res, var.vertical_res, 3)) #frame is numpy array as it is fasteer to edit and write data to

run = True
while run: #creates an indefinite loop to keep the game running
    display.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False #if the cross button is pressed, the window closes - allows exit of the program
        if event.type == VIDEORESIZE:
            var.screenX, var.screenY = display.get_size() #updates screen size, so that game scales to size of screens
            font = pygame.font.SysFont(None, int(var.screenX * 0.1))
    Raycast.RayCast(display, var.xPos, var.yPos, frame, var.player_rotation) #calls the raycast subroutine
    var.xPos, var.yPos, var.player_rotation = player.Movement(var.xPos, var.yPos, var.player_rotation, pygame.key.get_pressed()) #calls the movement subroutine
    audio.transform_sample(audio.audio_queue)
    text = font.render(f"current note: {var.note}", True, (255, 255, 255))
    display.blit(text, (var.screenX * 0.05, var.screenY * 0.05))
    print(list(var.recent_notes.queue))
    pygame.display.update() #updates the display