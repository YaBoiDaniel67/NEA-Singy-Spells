import pygame
import numpy as np
screenX, screenY = 320, 180 #initial window size
display = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)
player_rotation = 0 #players rotation
xPos, yPos = (3, 3) #players coords
horizontal_res = 120 #horizontal resolution
vertical_res = 200 #vertical resolution
halfvertical_res = int(vertical_res / 2) #half the vertical resolution
pixels_per_degree = horizontal_res/60 #scale factor - FOV is 60deg
world_map = [[1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 1, 1, 1, 1],
             [1, 0, 0, 0, 1],
             [1, 1, 1, 1, 1]]

melody_list = ["Happy Birthday", "Twinkle Twinkle Little Star"]

note = "-" #current note being detected
humming = False #whether the note is being hummed
recent_notes = [] #what notes have been seen recently
current_melody = np.array([], dtype = object) #what melody is the player currently singing
potential_melody = [] #what melodies the algorithm has detected the player singing
audio_start_time = 0
note_start_time = 0
new_note_start_time = None
prev_frame_note = 0
candidate_note = None
melody_lock = False

projectiles = []
depth = np.zeros(horizontal_res)