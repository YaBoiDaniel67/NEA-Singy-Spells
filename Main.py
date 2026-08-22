import pygame
from pygame.locals import *
import numpy as np
#imports all librarys needed for this file
import Raycaster as Raycast
import Player as player
import Audio.Audio_Input as audio
import Audio.Melody_Detector as melody
import Graphics.Texture_load as textures
import spells
#imports the other files

screenX, screenY = 320, 180 #initial window size
display = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)
game_state = "Main Menu"

player_rotation = 0 #players rotation
xPos, yPos = (1.1, 1.1) #players coords
horizontal_res = 120 #horizontal resolution
vertical_res = 200 #vertical resolution
half_vertical_res = int(vertical_res / 2) #half the vertical resolution
pixels_per_degree = horizontal_res/60 #scale factor - FOV is 60deg
depth = np.zeros(horizontal_res)
world_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 1],
             [1, 1, 1, 1, 1]]

pygame.font.init()
note_display_font = pygame.font.SysFont(None, int(screenX * 0.05))
Main_Menu_Title_font = pygame.font.SysFont(None, int(screenX * 0.5))

clock = pygame.time.Clock()
frame = np.random.uniform(0, 1, (horizontal_res, vertical_res, 3)) #frame is numpy array as it is fasteer to edit and write data to

texture_dict = textures.load_textures(half_vertical_res)

last_singing_time = 0
singing = False

note = "-" #current note being detected
humming = False #whether the note is being hummed
recent_notes = [] #what notes have been seen recently
current_melody = np.array([], dtype = object) #what melody is the player currently singing
potential_melody = [] #what melodies the algorithm has detected the player singing
melody_lock = False
audio_start_time = 0
melody_list = ["Happy Birthday", "Twinkle Twinkle Little Star"]
last_melody_check = 0
note_start_time = 0
new_note_start_time = None
prev_frame_note = 0
candidate_note = None

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
active_spells = []

start_button = Button(screenX / 2 - (texture_dict["play_button"].get_width() / 2), screenY / 1.75 - (texture_dict["play_button"].get_height() / 2), screenX / 10, screenX / 10, texture_dict["play_button"], display)
start_text = Main_Menu_Title_font.render("Singy Spells", True, (0, 0, 0))

run = True

#MAIN PROGRAM LOOP STARTS HERE
while run: #creates an indefinite loop to keep the game running
    display.fill((0, 0, 0))
    for event in pygame.event.get():
      if event.type == QUIT:
         run = False #if the cross button is pressed, the window closes - allows exit of the program
      if event.type == VIDEORESIZE:
         screenX, screenY = display.get_size() #updates screen size, so that game scales to size of screens
         start_button.width, start_button.height = screenX / 10, screenX / 10
         start_button.x, start_button.y = screenX / 2  - (start_button.width / 2), screenY / 1.75 - (start_button.height / 2)
         note_display_font = pygame.font.SysFont(None, int(screenX * 0.05))
         Main_Menu_Title_font = pygame.font.SysFont(None, (int(screenX * 0.5)))
      if event.type == KEYDOWN:
         if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            game_state = "Main Menu"
         elif pygame.key.get_pressed()[pygame.K_f]:
            active_spells.append(spells.Star(10, 0.01, xPos, yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Star"], "projectile", False))
    match game_state:
     case "Main Menu":
       frame, depth = Raycast.RayCast(2, 2, frame, world_map, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
       player_rotation += 0.001
       display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen
       display.blit(pygame.transform.scale(start_text, (screenX * 0.5, screenX * 0.125)), (screenX * 0.25, screenY * 0.125)) 
       start_button.draw_to_screen()
       if start_button.check_pressed():
          game_state = "Play"
          xPos, yPos, player_rotation = 1.1, 1.1, 0
     case "Play":
      frame, depth = Raycast.RayCast(xPos, yPos, frame, world_map, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
      xPos, yPos, player_rotation = player.Movement(xPos, yPos, world_map, player_rotation, pygame.key.get_pressed(), humming) #calls the movement subroutine
      note, humming, recent_notes, current_melody, melody_lock, audio_start_time, last_singing_time, singing = audio.transform_sample(audio.audio_queue, recent_notes, current_melody, melody_lock, note, humming, audio_start_time, last_singing_time, singing)
      note_text = note_display_font.render(f"current note: {note}", True, (0, 0, 0))
      current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note  = melody.determine_melody(note, recent_notes, current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note)
      current_melody, melody_lock, potential_melody, last_melody_check = melody.check_melody(current_melody, melody_lock, potential_melody, last_melody_check)
      active_spells, potential_melody = spells.find_spell(horizontal_res, pixels_per_degree, player_rotation, xPos, yPos, texture_dict, screenX, potential_melody, active_spells)
      for spell in active_spells:
        frame, active_spells = spells.draw_on_screen(frame, spell, world_map, xPos, yPos, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, active_spells)
      display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen
      display.blit(note_text, (screenX * 0.05, screenY * 0.05)) #draws the current note text to screen
    pygame.display.update() #updates the display
    clock.tick(80) #caps FPS at 80