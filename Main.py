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
world_map = np.random.choice([0], (10, 10)) #creates the world map
world_map[0, :] = 1 #sets all map borders to 1 to prevent errors
world_map[-1, :] = 1
world_map[:, 0] = 1
world_map[:, -1] = 1

pygame.font.init()
note_display_font = pygame.font.SysFont(None, int(screenX * 0.05))
Main_Menu_Title_font = pygame.font.SysFont(None, int(screenX * 0.5))

clock = pygame.time.Clock()
frame = np.random.uniform(0, 1, (horizontal_res, vertical_res, 3)) #frame is numpy array as it is faster to edit and write data to

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

settings_buttons = []
return_button = Buttons.Button(screenX, screenY, texture_dict["return_button"], display, 0.04, 0.07, 0.06, 0.06, None)
settings_buttons.append(return_button)
all_buttons.append(return_button)
mic_options_button = Buttons.Button(screenX, screenY, texture_dict["microphone_button"], display, 0.5, 0.125, 0.3, 0.111, "Microphone")
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
      if event.type == VIDEORESIZE: #if the screen changes size
         screenX, screenY = display.get_size() #updates screen size, so that game scales to size of screens
         for buttons in all_buttons: #loops through all buttons that currently exist
            buttons.resize(screenX, screenY) #calls the resize subroutine, inputting new screenX and Y
         for buttons in current_mics:
            buttons.resize(screenX, screenY)
         note_display_font = pygame.font.SysFont(None, int(screenX * 0.05)) #resizes font for displaying note
         Main_Menu_Title_font = pygame.font.SysFont(None, (int(screenX * 0.5))) #resizes font for menu title
      if event.type == KEYDOWN: #if any key is activly being pressed
         if pygame.key.get_pressed()[pygame.K_ESCAPE]: #if the escape key is pressed
            match game_state:
             case "Play": #if current game state is playing
              game_state = "Main Menu" #moves to main menud state
              menu_state = "Main" #sets menu state to main
             case "settings": #if current menu state is in settings
               menu_state = "Main" #move to main menu state
             case "microphone_select": #if menu states is in microphone settings
               menu_state = "settings" #moves to settings menu state
         elif pygame.key.get_pressed()[pygame.K_f]:
            active_spells.append(spells.Invis_Projectile(10, 0.05, Player.xPos, Player.yPos, spells.get_ray_angle(horizontal_res, pixels_per_degree, Player.rotation, screenX), texture_dict["Invis_texture"], "projectile", 0.5, 10, spells.ground_cactus, texture_dict["cactus"], 0.5))
    match game_state:
     case "Main Menu": #if the game is currently in main menu state
        if stream_open[0] == True: #checks if stream is open
           stream_open[0] = False #closes the stream
        frame, depth = Raycast.RayCast(Player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
        Player.rotation += 0.001 #adds a little bit to player rotation, so the screen slowely rotates
        display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen 
        match menu_state:
         case "Main": #if the menu state is main
          display.blit(pygame.transform.scale(start_text, (screenX * 0.5, screenX * 0.125)), (screenX * 0.25, screenY * 0.125))
          for button in main_menu_buttons:
             button.draw_to_screen() #draws all main menu buttons to screen
          if start_button.check_pressed(): #checks if the start button got pressed
             game_state = "Play" #sets game state to play
             Player.xPos, Player.yPos, Player.rotation, active_spells = 1.1, 1.1, 0, [] #initalises variable for gameplay
          elif main_settings_button.check_pressed(): #if the settings button got pressed
             menu_state = "settings" #sets the menu state to settings
             return_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed when clicking on settings
         case "settings": #if the menu state is in settings
           for buttons in settings_buttons:
              buttons.draw_to_screen() #draws all the settings button to the screen
           if mic_options_button.check_pressed(): #if the mic options button got pressed
              menu_state = "microphone_select" #sets menu state to microphone select
              return_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed
              current_mics, mic_dict = settings.find_mic_options(screenX, screenY, display, texture_dict) #finds all currently available microphones
           if return_button.check_pressed(): #if the return button got pressed
              menu_state = "Main" #sets menu state to main
              main_settings_button.last_press = time.monotonic() #sets the returns button last press time so it doesnt accidently get pressed when clicking on return
         case "microphone_select": #if menu state is in microphone select
           mic_preference = settings.display_mic_options(current_mics, mic_dict, mic_preference, texture_dict) #draws all the current mic options to the screen
           return_button.draw_to_screen() #draws return button
           if return_button.check_pressed(): #if the return button got pressed
              menu_state = "settings" #sets menu state to settings
     case "Play":
       if stream_open[0] == False: #if the stream is closed
          stream_open[0] = True #allows the stream to open
          audio_queue, stream = audio.open_stream(mic_preference) #opens the stream with mic preference
          threaded_audio = threading.Thread(target = audio.collect_sample, args = (audio_queue, stream, stream_open), daemon = True) #creates a thread so that the audio detection can run in parallel with the rest of the project
          threaded_audio.start() #starts the thread
       frame, depth = Raycast.RayCast(Player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, texture_dict["sky"], texture_dict["wall"], depth, texture_dict["floor"]) #calls the raycast subroutine
       Player.Movement(world_map, pygame.key.get_pressed()) #calls the movement subroutine
       note, humming, recent_notes, current_melody, melody_lock, audio_start_time, last_singing_time, singing = audio.transform_sample(audio_queue, recent_notes, current_melody, melody_lock, note, humming, audio_start_time, last_singing_time, singing)
       note_text = note_display_font.render(f"current note: {note}, {humming}", True, (0, 0, 0))
       current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note  = melody.determine_melody(note, recent_notes, current_melody, note_start_time, candidate_note, new_note_start_time, prev_frame_note)
       current_melody, melody_lock, potential_melody, last_melody_check = melody.check_melody(current_melody, melody_lock, potential_melody, last_melody_check)
       active_spells, potential_melody = spells.find_spell(horizontal_res, pixels_per_degree, Player.rotation, Player.xPos, Player.yPos, texture_dict, screenX, potential_melody, active_spells)
       for spell in active_spells:
         frame, active_spells = spells.draw_on_screen(frame, spell, world_map, Player.xPos, Player.yPos, Player.rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, active_spells)
       active_spells = spells.sort_spell_list(Player.xPos, Player.yPos, active_spells)
       display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (screenX, screenY)), (0, 0)) #draws the values stored in frame to the screen
       display.blit(note_text, (screenX * 0.05, screenY * 0.05)) #draws the current note text to screen
    pygame.display.update() #updates the display
    clock.tick(80) #caps FPS at 80