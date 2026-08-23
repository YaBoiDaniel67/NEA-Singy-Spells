import pygame
from pygame.locals import *
import numpy as np
import threading
import pyaudio
#imports all librarys needed for this file
import Raycaster as Raycast
import Player as player
import Audio.Audio_Input as audio
import Audio.Melody_Detector as melody
import Graphics.Texture_load as textures
import spells
import Button as Buttons
import Settings_Menu as settings
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

active_spells = []
current_mics, mic_dict = [], []
audio_instance = pyaudio.PyAudio()
mic_preference = audio_instance.get_default_input_device_info()["index"]
audio_instance.terminate()
stream = None
stream_open = True

menu_state = "Main"
all_buttons = []
main_menu_buttons = []
start_button = Buttons.Button(screenX, screenY, texture_dict["play_button"], display, 0.5, 4 / 7, 0.1, 0.1, None)
main_menu_buttons.append(start_button)
all_buttons.append(start_button)
main_settings_button = Buttons.Button(screenX, screenY, texture_dict["settings_button"], display, 0.03, 0.05, 0.06, 0.06, None)
main_menu_buttons.append(main_settings_button)
all_buttons.append(main_settings_button)

settings_buttons = []
mic_options_button = Buttons.Button(screenX, screenY, texture_dict["microphone_button"], display, 0.5, 0.1, 0.3, 0.111, None)
settings_buttons.append(mic_options_button)
all_buttons.append(mic_options_button)

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
         for buttons in all_buttons:
            buttons.resize(screenX, screenY)
         note_display_font = pygame.font.SysFont(None, int(screenX * 0.05))
         Main_Menu_Title_font = pygame.font.SysFont(None, (int(screenX * 0.5)))
      if event.type == KEYDOWN:
         if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            if game_state == "Play":
              game_state = "Main Menu"
              menu_state = "Main"
            elif menu_state == "settings":
               menu_state = "Main"
            elif menu_state == "microphone_select":
               menu_state = "settings"
         elif pygame.key.get_pressed()[pygame.K_f]:
            active_spells.append(spells.Star(10, 0.01, xPos, yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Star"], "projectile", False))
    match game_state:
     case "Main Menu":
        if stream_open == True:
           stream_open = False
        frame, depth = Raycast.RayCast(2, 2, frame, world_map, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
        player_rotation += 0.001
        display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen 
        if menu_state == "Main":
          display.blit(pygame.transform.scale(start_text, (screenX * 0.5, screenX * 0.125)), (screenX * 0.25, screenY * 0.125))
          for button in main_menu_buttons:
             button.draw_to_screen()
          if start_button.check_pressed():
             game_state = "Play"
             xPos, yPos, player_rotation, active_spells = 1.1, 1.1, 0, []
          elif main_settings_button.check_pressed():
             menu_state = "settings"
        elif menu_state == "settings":
           for buttons in settings_buttons:
              buttons.draw_to_screen()
           if mic_options_button.check_pressed():
              menu_state = "microphone_select"
              current_mics, mic_dict = settings.find_mic_options(screenX, screenY, display, texture_dict)
        elif menu_state == "microphone_select":
           mic_preference = settings.display_mic_options(current_mics, mic_dict, mic_preference, texture_dict)
     case "Play":
       if stream_open == False:
          stream_open = True
          audio_queue, stream = audio.open_stream(mic_preference)
          threaded_audio = threading.Thread(target = audio.collect_sample, args = (audio_queue, stream, stream_open), daemon = True) #creates a thread so that the audio detection can run in parallel with the rest of the project
          threaded_audio.start() #starts the thread
       frame, depth = Raycast.RayCast(xPos, yPos, frame, world_map, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
       xPos, yPos, player_rotation = player.Movement(xPos, yPos, world_map, player_rotation, pygame.key.get_pressed(), humming) #calls the movement subroutine
       note, humming, recent_notes, current_melody, melody_lock, audio_start_time, last_singing_time, singing = audio.transform_sample(audio_queue, recent_notes, current_melody, melody_lock, note, humming, audio_start_time, last_singing_time, singing)
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