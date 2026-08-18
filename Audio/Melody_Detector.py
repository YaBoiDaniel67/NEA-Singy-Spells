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
  intervals = [] #defines an empty list to store itnervals
  for i in range(1, len(melody)): #starts at 1 so it can compare indexes 1 and 0 for the first interval
    intervals.append(melody[i][0] - melody[i - 1][0]) #calculates the interval between the notes and adds it to the interval list
  return intervals

def determine_times(melody):
  game_times = []
  for i in range(len(melody)):
    game_times.append(melody[i][1]) #adds the time value from the input to game_times
  return game_times

def check_melody():
  global melody_when_added #declares melody when added as a global variable
  if len(var.current_melody) > 1: #if current melody holds sufficient data to be a melody
    player_intervals = determine_interval(var.current_melody) #finds the intervals between the players notes
    player_times = []
    for i in range(len(var.current_melody)):
      player_times.append(var.current_melody[i][1])
    player_times = list(np.array(player_times) / sum(player_times))
    for i, melody in game_melodies.items():
      if len(var.current_melody) >= len(melody) and melody_when_added != str(player_intervals):
        print(var.current_melody)
        game_intervals = determine_interval(melody) #finds the intervals between the games notes
        game_times = determine_times(melody)
        game_times = list(np.array(game_times) / sum(game_times))
        min_correct_time = max(int(len(game_times) * 0.75), 1)
        min_interval_num = len(game_intervals)
        allowed_wrong = int(len(game_intervals) * 0.5) #calculates how many wrong intervals the player is allowed
        min_correct_interval = max(int(len(game_intervals) * 0.75), 1) #calculates how many correct intervals the player must have
        best_wrong = 999
        best_correct = 0
        best_time_wrong = 999
        best_time_correct = 0
        if len(player_times) >= len(game_times):
          for j in range(len(player_times) - len(game_times) + 1):
            correct_time = 0
            wrong_time = 0
            for k in range(len(game_times)):
              if abs(player_times[j + k] - game_times[k]) <= 0.3:
                correct_time += 1
              else:
                wrong_time += 1
                if wrong_time > min_correct_time:
                  break
            if wrong_time < best_time_wrong:
              best_time_wrong = wrong_time
              best_time_correct = correct_time
        else:
          best_time_correct = 0
        for j in range(len(player_intervals) - min_interval_num + 1):
          wrong_interval = 0
          correct_interval = 0
          for k in range(min_interval_num):
            if abs(player_intervals[j + k] - game_intervals[k]) <= 1:
              correct_interval += 1
            else:
              wrong_interval += 1
              if wrong_interval > allowed_wrong:
                break
          if wrong_interval < best_wrong:
            best_wrong = wrong_interval
            best_correct = correct_interval
        if best_correct >= min_correct_interval and best_time_wrong <= allowed_wrong: #if there are enoguh correct intervals and times
          potential_melody.append(i) #adds the melody ID to potential_melody
          melody_when_added = str(player_intervals) #figures out the seocnd to last item of current_melody and saves it