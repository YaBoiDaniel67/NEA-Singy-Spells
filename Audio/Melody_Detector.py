import Variables as var
import numpy as np
import time
import csv_reader as csv

game_melodies = csv.load_csv_for_reading("Audio/Melody_Data.csv")
potential_melody = []

def determine_melody():
  if var.recent_notes: #if there are any recent notes
    print(var.current_melody)
    local_recent_note = var.recent_notes[-1][0] % 12 #takes the most recent detcted note, and scales it down to 1 octave
    if len(var.current_melody) > 5: #if the saved melody is getting too long
       var.current_melody = var.current_melody[1:] #removes the oldest value in the melody
    if len(var.current_melody) > 0: #if current melody contains any values
      if var.current_melody[-1][0] == local_recent_note or np.abs(var.recent_notes[-1][1] - var.current_melody[-1][2]) <= 20: #if the note has not changed
        var.current_melody[-1][1] = time.monotonic() - var.note_start_time #update the time the note has been held
        var.candidate_note = None
        var.new_note_start_time = None
      else:
        if var.candidate_note is None: #if there is no candidate note
          if var.prev_frame_note == local_recent_note: #if the previous frames note is the same as the current, ensures note is stable as it lasts for multiple frames
            var.candidate_note = local_recent_note #set candidate note
            var.new_note_start_time = time.monotonic() #set the start of this new note
            var.note_start_time = time.monotonic() #set the start of the melody
            return
          var.prev_frame_note = local_recent_note #runs if there was no prev frame note, sets one
        if var.candidate_note == local_recent_note: #if the note is consistent
          if time.monotonic() - var.new_note_start_time > 0.1: #if it has lasted for a reasonable amount of time
            melody_copy = list(var.current_melody) #creates a list version of current melody
            melody_copy.append(np.array([local_recent_note, 0, var.recent_notes[-1][1]], dtype = object)) #appends the note array to that local list copy
            var.current_melody = np.array(melody_copy, dtype = object) #sets current melody to the array version of the local list
            var.new_note_start_time = None #resets new note start time
            var.candidate_note = None #resets candidate note
        else:
          var.candidate_note = None #resets candidate note
          var.new_note_start_time = None #resets new note start time
    else:
      melody_copy = list(var.current_melody) #creates a list version of current melody
      melody_copy.append(np.array([local_recent_note, 0, var.recent_notes[-1][1]], dtype = object)) #appends the note array to that local list copy
      var.current_melody = np.array(melody_copy, dtype = object) #sets current melody to the array version of the local list
      var.note_start_time = time.monotonic() #sets note start time

def check_melody():
  if len(var.current_melody) > 0:
    for i in range(0, len(game_melodies)):
      if game_melodies[i][0][0] == var.current_melody[-1][0]:
        for j in range(len(game_melodies[i])):
          if j < len(var.current_melody):
           if np.abs(game_melodies[i][j][0] - var.current_melody[-(1 + j)][0]) == 1:
            continue
           elif game_melodies[i][j][0] == var.current_melody[-(1 + j)][0]:
             match = True
           else:
             match = False
             return
          else:
            return
        if match == True and i not in potential_melody:
          potential_melody.append(i)
    print(potential_melody)
