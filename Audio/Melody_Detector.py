import Variables as var
import numpy as np
import time

def determine_melody():
    print(var.current_melody)
    local_recent_notes = list(np.array(var.recent_notes) % 12)
    local_recent_notes.append(-1)
    while local_recent_notes[0] != -1:
        if len(var.current_melody) > 5:
           var.current_melody = var.current_melody[1:]
        if len(var.current_melody) >= 2:
           if var.current_melody[-2][0] == var.current_melody[-1][0]:
              var.current_melody[-2][1] += var.current_melody[-1][1]
              var.current_melody = var.current_melody[:-1] 
        if len(var.current_melody) != 0:
          if var.current_melody[-1][0] == local_recent_notes[0]:
            var.current_melody[-1][1] = time.monotonic() - var.melody_start_time
            local_recent_notes.pop(0)
            var.candidate_note = None
            var.new_note_start_time = None
            continue
        if var.candidate_note == None:
            var.candidate_note = local_recent_notes[0]
            var.new_note_start_time = time.monotonic()
            local_recent_notes.pop(0)
            continue
        if var.candidate_note == local_recent_notes[0]:
          if time.monotonic() - var.new_note_start_time > 0.1:
            melody_copy = list(var.current_melody)
            melody_copy.append(np.array([local_recent_notes.pop(0), 0], dtype = object))
            var.current_melody = np.array(melody_copy, dtype = object)
            var.melody_start_time = time.monotonic() 
            var.new_note_start_time = None
            continue
        local_recent_notes.pop(0)