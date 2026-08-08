import Variables as var
import numpy as np
import time

def determine_melody():
    local_recent_notes = list(np.array(var.recent_notes) % 12)
    local_recent_notes.append(-1)
    while local_recent_notes[0] != -1:
        if len(var.current_melody) != 0:
          if local_recent_notes[0] != local_recent_notes[1] and local_recent_notes[1] != var.current_melody[-1][0]:
            if var.current_melody[-1][0] != local_recent_notes[0]:
              var.current_melody = np.append(var.current_melody, np.array([local_recent_notes.pop(0), 0]))
              var.melody_start_time = time.monotonic()
            else:
              local_recent_notes.pop(0)
              if time.monotonic() - var.melody_start_time > 0.1:
                var.current_melody[-1][1] += 0.1
          else:
            local_recent_notes.pop(0)
        else:
          var.current_melody = np.append(var.current_melody, np.array([local_recent_notes.pop(0), 0]))
        if len(var.current_melody) > 5:
           var.current_melody.pop(0)
    false_values = []
    for i in range(len(var.current_melody)):
       if var.current_melody[i][1] < 10:
          false_values.append(var.current_melody[i])
    var.current_melody = (np.array(var.current_melody)[np.isin(np.array(var.current_melody).astype(int), np.array(false_values).astype(int))])
    print(var.current_melody)