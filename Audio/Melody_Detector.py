import Variables as var
import numpy as np
import time

def determine_melody():
        if not var.recent_notes:
           return
        print(var.current_melody)
        local_recent_note = var.recent_notes[-1] % 12
        if len(var.current_melody) > 5:
           var.current_melody = var.current_melody[1:]
        if len(var.current_melody) >= 2:
           if var.current_melody[-2][0] == var.current_melody[-1][0]:
              var.current_melody[-2][1] += var.current_melody[-1][1]
              var.current_melody = var.current_melody[:-1] 
        if len(var.current_melody) > 0:
          if var.current_melody[-1][0] == local_recent_note:
            var.current_melody[-1][1] = time.monotonic() - var.melody_start_time
            var.candidate_note = None
            var.new_note_start_time = None
            return
          if var.candidate_note is None:
            if var.prev_frame_note == local_recent_note:
              var.candidate_note = local_recent_note
              var.new_note_start_time = time.monotonic()
              var.melody_start_time = time.monotonic() 
              return
            var.prev_frame_note = local_recent_note
          if var.candidate_note == local_recent_note:
            if time.monotonic() - var.new_note_start_time > 0.1:
              melody_copy = list(var.current_melody)
              melody_copy.append(np.array([local_recent_note, 0], dtype = object))
              var.current_melody = np.array(melody_copy, dtype = object)
              var.new_note_start_time = None
              var.candidate_note = None
              return
          if local_recent_note != var.candidate_note:
            var.candidate_note = None
            var.new_note_start_time = None
          return
        melody_copy = list(var.current_melody)
        melody_copy.append(np.array([local_recent_note, 0], dtype = object))
        var.current_melody = np.array(melody_copy, dtype = object)
        var.melody_start_time = time.monotonic()
        