import pygame
from pygame.locals import *
import numpy as np
#imports all librarys needed for this file
import Raycaster as Raycast
import Player as player
import Variables as var
import Audio.Audio_Input as audio
import Audio.Melody_Detector as melody
import Graphics.Texture_load as textures
import spells
#imports the other files

pygame.font.init()
note_display_font = pygame.font.SysFont(None, int(var.screenX * 0.05))
Main_Menu_Title_font = pygame.font.SysFont(None, (int(var.screenX * 0.5)))

display = var.display
clock = pygame.time.Clock()
frame = np.random.uniform(0, 1, (var.horizontal_res, var.vertical_res, 3)) #frame is numpy array as it is fasteer to edit and write data to

class Button():
   def __init__(self, x, y, width, height, surface, blit_surface):
      self.x = x 
      self.y = y
      self.width, self.height = width, height
      self.surface = surface
      self.blit_surface = blit_surface

   def draw_to_screen(self):
      display.blit(pygame.transform.scale(self.surface, (self.width, self.height)), (self.x, self.y))

   def check_pressed(self):
      pressed = False
      if pygame.mouse.get_pressed()[0] == True:
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height:
           pressed = True
      return pressed

start_button = Button(var.screenX / 2 - (textures.play_button.get_width() / 2), var.screenY / 1.75 - (textures.play_button.get_height() / 2), var.screenX / 10, var.screenX / 10, textures.play_button, display)
start_text = Main_Menu_Title_font.render("Singy Spells", True, (0, 0, 0))

run = True
while run: #creates an indefinite loop to keep the game running
    display.fill((0, 0, 0))
    for event in pygame.event.get():
      if event.type == QUIT:
         run = False #if the cross button is pressed, the window closes - allows exit of the program
      if event.type == VIDEORESIZE:
         var.screenX, var.screenY = display.get_size() #updates screen size, so that game scales to size of screens
         start_button.width, start_button.height = var.screenX / 10, var.screenX / 10
         start_button.x, start_button.y = var.screenX / 2  - (start_button.width / 2), var.screenY / 1.75 - (start_button.height / 2)
         note_display_font = pygame.font.SysFont(None, int(var.screenX * 0.05))
         Main_Menu_Title_font = pygame.font.SysFont(None, (int(var.screenX * 0.5)))
      if event.type == KEYDOWN:
         if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            var.game_state = "Main Menu"
    match var.game_state:
     case "Main Menu":
       frame = Raycast.RayCast(2, 2, frame, var.player_rotation) #calls the raycast subroutine
       var.player_rotation += 0.001
       display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (var.screenX, var.screenY)), (0, 0)) #draws the values stored in frame to the screen
       display.blit(pygame.transform.scale(start_text, (var.screenX * 0.5, var.screenX * 0.125)), (var.screenX * 0.25, var.screenY * 0.125)) 
       start_button.draw_to_screen()
       if start_button.check_pressed():
          var.game_state = "Play"
          var.xPos, var.yPos, var.player_rotation = 1.1, 1.1, 0
     case "Play":
      frame = Raycast.RayCast(var.xPos, var.yPos, frame, var.player_rotation) #calls the raycast subroutine
      var.xPos, var.yPos, var.player_rotation = player.Movement(var.xPos, var.yPos, var.player_rotation, pygame.key.get_pressed()) #calls the movement subroutine
      audio.transform_sample(audio.audio_queue)
      note_text = note_display_font.render(f"current note: {var.note}", True, (255, 255, 255))
      melody.determine_melody()
      melody.check_melody()
      spells.find_spell()
      for spell in var.spells:
        frame = spells.draw_on_screen(frame, spell)
      display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (var.screenX, var.screenY)), (0, 0)) #draws the values stored in frame to the screen
      display.blit(note_text, (var.screenX * 0.05, var.screenY * 0.05)) #draws the current note text to screen
    pygame.display.update() #updates the display
    clock.tick(80) #caps FPS at 80