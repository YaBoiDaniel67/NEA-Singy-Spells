import Variables as var
import numpy as np
import time

def determine_melody():
    local_recent_notes = list(np.array(var.recent_notes) % 12)
    local_recent_notes.append(-1)
    while local_recent_notes[0] != -1:
        if len(var.current_melody) > 5:
           var.current_melody = var.current_melody[1:]
        if len(var.current_melody) >= 2:
           if var.current_melody[-2][1] < 0.01:
             melody_copy = list(var.current_melody)
             del melody_copy[-2]
             var.current_melody = np.array(melody_copy, dtype = object)
           elif var.current_melody[-2][0] == var.current_melody[-1][0]:
              var.current_melody[-2][1] += var.current_melody[-1][1]
              var.current_melody = var.current_melody[:-1] 
        if len(var.current_melody) != 0:
          if var.current_melody[-1][0] != local_recent_notes[0]:
              melody_copy = list(var.current_melody)
              melody_copy.append(np.array([local_recent_notes.pop(0), 0], dtype = object))
              var.current_melody = np.array(melody_copy, dtype = object)
              var.melody_start_time = time.monotonic()
          else:
              local_recent_notes.pop(0)
              var.current_melody[-1][1] = time.monotonic() - var.melody_start_time
        else:
          melody_copy = list(var.current_melody)
          melody_copy.append(np.array([local_recent_notes.pop(0), 0], dtype = object))
          var.current_melody = np.array(melody_copy, dtype = object)
           
    print(var.current_melody)