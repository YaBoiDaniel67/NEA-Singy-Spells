import Variables as var
import numpy as np
import time
import csv_reader as csv

game_melodies = csv.load_csv_for_reading("Audio/Melody_Data.csv") #sets game_melodies to the interpreted values form the csv file storing melodies

melody_when_added = ""
last_melody_check = 0

def determine_melody():
  if var.recent_notes and var.note != "-": #if there are any recent notes, and a note is activly being sung
    local_recent_note = var.recent_notes[-1][0] % 12 #takes the most recent detcted note, and scales it down to 1 octave
    if len(var.current_melody) > 25: #if the saved melody is getting too long
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
            return
          var.prev_frame_note = local_recent_note #runs if there was no prev frame note, sets one
        if var.candidate_note == local_recent_note: #if the note is consistent
          if time.monotonic() - var.new_note_start_time > 0.1: #if it has lasted for a reasonable amount of time
            if len(var.current_melody) > 0:
              var.current_melody[-1][1] = time.monotonic() - var.note_start_time #updates the notes time held to ensure it is fully accurate
            melody_copy = list(var.current_melody) #creates a list version of current melody
            melody_copy.append(np.array([local_recent_note, 0, var.recent_notes[-1][1]], dtype = object)) #appends the note array to that local list copy
            var.current_melody = np.array(melody_copy, dtype = object) #sets current melody to the array version of the local list
            var.note_start_time = time.monotonic()
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
  intervals = [] #defines an empty list to store intervals
  for i in range(1, len(melody)): #starts at 1 so it can compare indexes 1 and 0 for the first interval
    intervals.append(melody[i][0] - melody[i - 1][0]) #calculates the interval between the notes and adds it to the interval list
  return intervals

def determine_times(melody):
  game_times = [] #define an empty list to store game times
  for i in range(len(melody)):
    game_times.append(melody[i][1]) #adds the time value from the input to game_times
  return game_times

def check_melody():
  global last_melody_check #declares last_melody_check as a global variable
  if time.monotonic() - last_melody_check < 0.05: #prevents the loop running too many times, boosting performance slightly
    return
  last_melody_check = time.monotonic()
  global melody_when_added #declares melody when added as a global variable
  if len(var.current_melody) > 1: #if current melody holds sufficient data to be a melody
    player_intervals = determine_interval(var.current_melody) #finds the intervals between the players notes
    player_times = [] #empties player tiems
    for i in range(len(var.current_melody)): #loops through all notes currently in var.current_melody
      player_times.append(var.current_melody[i][1]) #adds the time to player times
    player_times = list(np.array(player_times) / sum(player_times)) #normalises player times so it is a ratio between the time and total time
    for i, melody in game_melodies.items(): #loops through all melodies in game_melodies
      if len(var.current_melody) >= len(melody) and not var.melody_lock: #if current melody is long enough to potentially be melody, and there is no melody lock active
        game_intervals = determine_interval(melody) #finds the intervals between the games notes
        game_times = determine_times(melody) #finds the times for each note
        game_times = list(np.array(game_times) / sum(game_times)) #normalises the times into ratio form
        min_correct_time = max(int(len(game_times) * 0.75), 1) #calculates the minimum number of correct times needed for the melody to be detected
        min_interval_num = len(game_intervals) #calculates the minimum nubmer of intervals needed for the melody
        allowed_wrong = int(len(game_intervals) * 0.25) #calculates how many wrong intervals the player is allowed
        min_correct_interval = max(int(len(game_intervals) * 0.75), 1) #calculates how many correct intervals the player must have
        best_wrong = 999 #initialises best_wrong
        best_correct = 0 #initialises best_correct
        best_time_wrong = 999 #initialises best_time_wrong
        if len(player_times) >= len(game_times): #if the player has enough times that it could be the melody
          for j in range(len(player_times) - len(game_times) + 1): #slides a window across player times, stopping when there are only a game times amount of times left
            correct_time = 0 #resets correct time
            wrong_time = 0 #resets wrong time
            for k in range(len(game_times)): #loops through all values of game_times
              if abs(player_times[j + k] - game_times[k]) <= 0.3: #if the time difference is small enough, allow it
                correct_time += 1 #adds one to correct time
              else: #if the timne difference is to big
                wrong_time += 1 #adds 1 to wrong time
                if wrong_time > min_correct_time: #if too many wrong times have been detected
                  break #exits the loop
            if wrong_time < best_time_wrong: #if this iteration has less wrongs than the previous least
              best_time_wrong = wrong_time #sets this as the new leat amount of wrongs
          for j in range(len(player_intervals) - min_interval_num + 1): #slides a window across player intervals, stopping when there is only a melodies amount of notes left
            wrong_interval = 0 #resets wrong_interval
            correct_interval = 0 #resets correct_interval
            for k in range(min_interval_num): #loops through all values in game_intervals
              if abs(player_intervals[j + k] - game_intervals[k]) <= 1: #if the players note is within 1 of where it should be it is allowed
                correct_interval += 1 #adds 1 to correct interval
              else: #if the difference in note sis more than 1
                wrong_interval += 1 #adds 1 to worng inte4rval
                if wrong_interval > allowed_wrong: #if the player has gotten too many intervals wrong
                  break #breaks the loop
            if wrong_interval < best_wrong: #if fewer wrong intervals have eben recorded than the previous fewest
              best_wrong = wrong_interval #saves least worng intervals so far to best_wrong
              best_correct = correct_interval #saves the most correct intervals so far to best_correct
        if best_correct >= min_correct_interval and best_time_wrong <= allowed_wrong: #if there are enoguh correct intervals and times
          var.potential_melody.append(i) #adds the melody ID to potential_melody
          var.melody_lock = True #activates the melody lock