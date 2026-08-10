import Variables as var
import numpy as np
import time
import csv_reader as csv

game_melodies = csv.load_csv_for_reading("Audio/Melody_Data.csv")
potential_melody = []

melody_when_added = ""

def determine_melody():
  if var.recent_notes and var.note != "-": #if there are any recent notes, and a note is activly being sung
    local_recent_note = var.recent_notes[-1][0] % 12 #takes the most recent detcted note, and scales it down to 1 octave
    if len(var.current_melody) > 10: #if the saved melody is getting too long
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

def determine_interval(melody):
  intervals = []
  for i in range(1, len(melody)):
    intervals.append(melody[i][0] - melody[i - 1][0])
  return intervals

def check_melody():
  global melody_when_added #declares melody when added as a global variable
  if len(var.current_melody) > 1: #if current melody holds sufficient data to be a melody
    player_intervals = determine_interval(var.current_melody) #finds the intervals between the players notes
    for i, melody in game_melodies.items():
      if len(var.current_melody) >= len(melody) and melody_when_added != str(player_intervals):
        print(potential_melody)
        game_intervals = determine_interval(melody) #finds the intervals between the games notes
        min_interval_num = min(len(game_intervals), len(player_intervals)) #finds the lower value to iterate over
        correct_interval = 0 #resets correct_interval variable
        wrong = 0 #resets wrong variable
        allowed_wrong = max(int(len(game_intervals) * 0.35), 1) #calculates how many wrong intervals the player is allowed
        min_correct_interval = max(int(len(game_intervals) * 0.65), 1) #calculates how many correct intervals the player must have
        for j in range(min_interval_num):
          target_interval = game_intervals[j] #specifies game interval being looked at in this iteration
          user_interval = player_intervals[-len(game_intervals) + j] #specifies player interval being looked at in this iteration
          if abs(target_interval - user_interval) <= 1: #if there is less than 1 note off
            correct_interval += 1
          else:
            wrong += 1
          if wrong > allowed_wrong:
            break
        if correct_interval >= min_correct_interval: #if there are enoguh correct intervals
          potential_melody.append(i) #adds the melody ID to potential_melody
          melody_when_added = str(player_intervals) #figures out the seocnd to last item of current_melody and saves it
          return