import pygame
from pygame.locals import *
import numpy as np
import threading
import pyaudio
import time
#imports all librarys needed for this file
import Raycaster as Raycast
import Player as player
import Audio.Audio_Input as audio
import Audio.Melody_Detector as melody
import Graphics.Texture_load as textures
import spells
import Button as Buttons
import Settings_Menu as settings
import file_reader
import on_screen_elements as all_objects
import Enemy
#imports the other files

screenX, screenY = 320, 180 #initial window size
display = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)
game_state = "Main Menu"
Player = player.Player()

horizontal_res = 120 #horizontal resolution
vertical_res = 200 #vertical resolution
half_vertical_res = int(vertical_res / 2) #half the vertical resolution
fov = 60
pixels_per_degree = horizontal_res/fov #scale factor
depth = np.zeros(horizontal_res) #creates an array of zeros the length of horizontal res
world_map = file_reader.extract_map(1)
texture_index_mappings = ["", "wall", "wall_target"]
tutorial_text = ["Placeholder Text", "Hey gang aint this fun", "tutorial time", "woopdeedoo"]
jump_list = [1, 2, 3, 100]

pygame.font.init()
note_display_font = pygame.font.SysFont(None, int(screenX * 0.05)) #initialises fonts. None gives default pygame fonta
Main_Menu_Title_font = pygame.font.SysFont(None, int(screenX * 0.5))
tutorial_text_font = pygame.font.SysFont(None, int(screenX * 0.05))

clock = pygame.time.Clock()
frame = np.random.uniform(0, 1, (horizontal_res, vertical_res, 3)) #frame is numpy array as it is faster to edit and write data to

texture_dict = textures.load_textures(half_vertical_res)
last_singing_time = 0
singing = False

note = "-" #current note being detected
humming = False #whether the note is being hummed
audio_queue = []
recent_notes = [] #what notes have been seen recently
current_melody = np.array([], dtype = object) #what melody is the player currently singing
potential_melody = [] #what melodies the algorithm has detected the player singing
melody_lock = False #whether this current singing has already detected a melody
audio_start_time = 0
last_melody_check = 0
note_start_time = 0
new_note_start_time = None
prev_frame_note = 0
candidate_note = None

on_screen_objects = []
enemy_list = []
current_mics, mic_dict = [], []
audio_instance = pyaudio.PyAudio() #initiates a pyaduio instance
mic_preference = audio_instance.get_default_input_device_info()["index"] #gets the devices defualt mic as the defualt preference
audio_instance.terminate() #terminates the instance
stream = None
stream_open = [True]

menu_state = "Main"
all_buttons = []
main_menu_buttons = []
start_button = Buttons.Button(screenX, screenY, texture_dict["play_button"], display, 0.5, 4 / 7, 0.1, 0.1, None)
main_menu_buttons.append(start_button)
all_buttons.append(start_button)
main_settings_button = Buttons.Button(screenX, screenY, texture_dict["settings_button"], display, 0.04, 0.07, 0.06, 0.06, None)
main_menu_buttons.append(main_settings_button)
all_buttons.append(main_settings_button)
Tutorial_button = Buttons.Button(screenX, screenY, texture_dict["play_button"], display, 0.04, 0.93, 0.06, 0.06, "Tutorial")
main_menu_buttons.append(Tutorial_button)
all_buttons.append(Tutorial_button)

settings_buttons = []
return_button = Buttons.Button(screenX, screenY, texture_dict["return_button"], display, 0.04, 0.07, 0.06, 0.06, None)
settings_buttons.append(return_button)
all_buttons.append(return_button)
mic_options_button = Buttons.Button(screenX, screenY, texture_dict["microphone_button"], display, 0.5, 0.125, 0.3, 0.111, "Microphone")
settings_buttons.append(mic_options_button)
all_buttons.append(mic_options_button)

start_text = Main_Menu_Title_font.render("Singy Spells", True, (0, 0, 0))

def initialise_variable(player, on_screen_objects):
  player.xPos, player.yPos, player.health, on_screen_objects = 2, 2, 100, [] #initalises variable for gameplay
  return on_screen_objects

def check_stream(mic_preference, audio_queue, stream, stream_open):
   if stream_open[0] == False: #if the stream is closed
      stream_open[0] = True #allows the stream to open
      audio_queue, stream = audio.open_stream(mic_preference) #opens the stream with mic preference
      threaded_audio = threading.Thread(target = audio.collect_sample, args = (audio_queue, stream, stream_open), daemon = True) #creates a thread so that the audio detection can run in parallel with the rest of the project
      threaded_audio.start() #starts the thread
   return audio_queue, stream

run = True
############################################################ MAIN PROGRAM LOOP STARTS HERE ############################################################
while run: #creates an indefinite loop to keep the game running
    display.fill((0, 0, 0)) #fills the screen with black
    for event in pygame.event.get():
      if event.type == QUIT:
         run = False #if the cross button is pressed, the window closes - allows exit of the program
      if event.type == VIDEORESIZE: #if the screen changes size
         screenX, screenY = display.get_size() #updates screen size, so that game scales to size of screens
         for buttons in all_buttons: #loops through all buttons that currently exist
            buttons.resize(screenX, screenY) #calls the resize subroutine, inputting new screenX and Y
         for buttons in current_mics: #loops through all the current mic buttons
            buttons.resize(screenX, screenY) #resizes them
         note_display_font = pygame.font.SysFont(None, int(screenX * 0.05)) #resizes font for displaying note
         Main_Menu_Title_font = pygame.font.SysFont(None, (int(screenX * 0.5))) #resizes font for menu title
         tutorial_text_font = pygame.font.SysFont(None, int(screenX * 0.05)) #resizes font for tutorial text
      if event.type == KEYDOWN: #if any key is activly being pressed
         if pygame.key.get_pressed()[pygame.K_ESCAPE]: #if the escape key is pressed
            match game_state:
             case "Play": #if current game state is playing
              game_state = "Main Menu" #moves to main menud state
              menu_state = "Main" #sets menu state to main
            match menu_state:
             case "settings": #if current menu state is in settings
               menu_state = "Main" #move to main menu state
             case "microphone_select": #if menu states is in microphone settings
               menu_state = "settings" #moves to settings menu state
         elif pygame.key.get_pressed()[pygame.K_f]:
            on_screen_objects.append(spells.Invis_Projectile(10, 0.05, Player.xPos, Player.yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, Player.rotation, screenX, fov), texture_dict["Invis_texture"], "projectile", 0.5, 10, spells.ground_cactus, texture_dict["cactus"], 0.5))
         elif pygame.key.get_pressed()[pygame.K_g]:
           on_screen_objects.append(spells.Star(10, 0.05, Player.xPos, Player.yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, Player.rotation, screenX, fov), texture_dict["Star"], "projectile", 0.5, False))
         elif pygame.key.get_pressed()[pygame.K_h]:
           on_screen_objects.append(spells.Fireball(20, 0.1, Player.xPos, Player.yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, Player.rotation, screenX, fov), texture_dict["Fireball"], "projectile", 1))
         elif pygame.key.get_pressed()[pygame.K_1]:
           on_screen_objects.append(Enemy.enemy(5, 100, 0.01, 0.5, 2, 2, texture_dict["Happy_guy"], 1, 0.1, enemy_list))
    match game_state:
     case "Main Menu": #if the game is currently in main menu state
        if stream_open[0] == True: #checks if stream is open
           stream_open[0] = False #closes the stream
        frame, depth = Raycast.RayCast(Player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, fov, texture_dict, texture_index_mappings, file_reader) #calls the raycast subroutine
        Player.rotation += 0.001 #adds a little bit to player rotation, so the screen slowely rotates
        display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen 
        match menu_state:
         case "Main": #if the menu state is main
          display.blit(pygame.transform.scale(start_text, (screenX * 0.5, screenX * 0.125)), (screenX * 0.25, screenY * 0.125)) #draws the start text to the screen
          for button in main_menu_buttons:
             button.draw_to_screen() #draws all main menu buttons to screen
          if start_button.check_pressed(): #checks if the start button got pressed
             game_state = "Play" #sets game state to play
             on_screen_objects = initialise_variable(Player, on_screen_objects)
             world_map = file_reader.extract_map(1)
          elif main_settings_button.check_pressed(): #if the settings button got pressed
             menu_state = "settings" #sets the menu state to settings
             return_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed when clicking on settings
          elif Tutorial_button.check_pressed():
             game_state = "Tutorial" #sets game state to play
             on_screen_objects = initialise_variable(Player, on_screen_objects)
             world_map = file_reader.extract_map(0)
             tutorial_stage = 0
             next_x = 3
             current_jump = 1
         case "settings": #if the menu state is in settings
           for buttons in settings_buttons:
              buttons.draw_to_screen() #draws all the settings button to the screen
           if mic_options_button.check_pressed(): #if the mic options button got pressed
              menu_state = "microphone_select" #sets menu state to microphone select
              return_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed
              current_mics, mic_dict = settings.find_mic_options(screenX, screenY, display, texture_dict) #finds all currently available microphones
           elif return_button.check_pressed(): #if the return button got pressed
              menu_state = "Main" #sets menu state to main
              main_settings_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed when clicking on return
         case "microphone_select": #if menu state is in microphone select
           mic_preference = settings.display_mic_options(current_mics, mic_dict, mic_preference, texture_dict) #draws all the current mic options to the screen
           return_button.draw_to_screen() #draws return button
           if return_button.check_pressed(): #if the return button got pressed
              menu_state = "settings" #sets menu state to settings
     case "Play":
       audio_queue, stream = check_stream(mic_preference, audio_queue, stream, stream_open)
       frame, depth = Raycast.RayCast(Player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, fov, texture_dict, texture_index_mappings, file_reader) #calls the raycast subroutine
       Player.Movement(world_map, pygame.key.get_pressed()) #calls the movement subroutine
       note, humming, recent_notes, current_melody, melody_lock, audio_start_time, last_singing_time, singing = audio.transform_sample(audio_queue, recent_notes, current_melody, melody_lock, note, humming, audio_start_time, last_singing_time, singing)
       note_text = note_display_font.render(f"current note: {note}, {humming}", True, (0, 0, 0))
       current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note  = melody.determine_melody(note, recent_notes, current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note)
       current_melody, melody_lock, potential_melody, last_melody_check = melody.check_melody(current_melody, melody_lock, potential_melody, last_melody_check)
       on_screen_objects, potential_melody = spells.find_spell(horizontal_res, pixels_per_degree, Player, texture_dict, screenX, potential_melody, on_screen_objects, fov)
       for current_object in on_screen_objects:
         frame, on_screen_objects, world_map = all_objects.draw_on_screen(frame, current_object, world_map, Player.xPos, Player.yPos, Player.rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, on_screen_objects, fov, Player)
         if current_object.type == "Spell":
           current_object.detect_hit(enemy_list, on_screen_objects)
       on_screen_objects = all_objects.sort_object_list(Player.xPos, Player.yPos, on_screen_objects)
       display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen
       display.blit(note_text, (screenX * 0.05, screenY * 0.05)) #draws the current note text to screen
       Player.display_health(display, screenX, screenY) #draws the player health bar to the screen
     case "Tutorial":
       audio_queue, stream = check_stream(mic_preference, audio_queue, stream, stream_open)
       if Player.xPos > next_x:
         next_x += jump_list[current_jump]
         current_jump += 1
         tutorial_stage += 1
       frame, depth = Raycast.RayCast(Player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, fov, texture_dict, texture_index_mappings, file_reader) #calls the raycast subroutine
       Player.Movement(world_map, pygame.key.get_pressed()) #calls the movement subroutine
       note, humming, recent_notes, current_melody, melody_lock, audio_start_time, last_singing_time, singing = audio.transform_sample(audio_queue, recent_notes, current_melody, melody_lock, note, humming, audio_start_time, last_singing_time, singing)
       note_text = note_display_font.render(f"current note: {note}, {humming}", True, (0, 0, 0))
       current_tutorial_stage_text = tutorial_text_font.render(tutorial_text[tutorial_stage], True, (0, 0, 0))
       current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note  = melody.determine_melody(note, recent_notes, current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note)
       current_melody, melody_lock, potential_melody, last_melody_check = melody.check_melody(current_melody, melody_lock, potential_melody, last_melody_check)
       on_screen_objects, potential_melody = spells.find_spell(horizontal_res, pixels_per_degree, Player, texture_dict, screenX, potential_melody, on_screen_objects, fov)
       for current_object in on_screen_objects:
         frame, on_screen_objects, world_map = all_objects.draw_on_screen(frame, current_object, world_map, Player.xPos, Player.yPos, Player.rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, on_screen_objects, fov, Player)
         if current_object.type == "Spell":
           current_object.detect_hit(enemy_list, on_screen_objects)
       on_screen_objects = all_objects.sort_object_list(Player.xPos, Player.yPos, on_screen_objects)
       display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen
       display.blit(note_text, (screenX * 0.05, screenY * 0.05)) #draws the current note text to screen
       display.blit(current_tutorial_stage_text, (screenX * 0.7, screenY * 0.05)) #draws the tutorial text to the screen
       Player.display_health(display, screenX, screenY) #draws the health bar to the screen
    pygame.display.update() #updates the display
    clock.tick(80) #caps FPS at 80