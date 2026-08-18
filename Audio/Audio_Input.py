import pyaudio
import threading
import numpy as np
from queue import Queue
import Audio.Hum_Detector
import Variables as var
import time

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
last_singing_time = 0
singing = False

audio_queue = Queue()
audio = pyaudio.PyAudio()
stream = audio.open(format = pyaudio.paInt16, #sets the data type as a 16 bit signed binary number
                     channels = 1, #sets the audio type as mono
                     rate = 16000, #sets the sample rate
                     input = True, #defines the stream as detecting sound from the mic
                     frames_per_buffer = 4096) #the amount of samples read in a given sample read

def collect_sample():
 while True:
  data = stream.read(4096) #reads 4096 samples from the stream
  audio_queue.put(data) #puts these samples in a queue

def transform_sample(input_queue):
 global last_singing_time
 global singing
 if not input_queue.empty(): #if the queue has sounds samples in it
  sample = input_queue.get() #get the set of samples and remove it from the queue
  sample = np.frombuffer(sample, dtype = np.int16) #converts the sample form binary numbers into decimal
  if 250 < np.mean(np.abs(sample)): #checks whether the average volume detected is loud enough, essentially blocking any background noises
    singing = True
    sample_magnitude = np.fft.rfft(sample) #applies an fft algorithm to the data of collect their magnitudes
    sample_magnitude = np.abs(sample_magnitude)
    sample_frequency = np.fft.rfftfreq(len(sample), 1.0 / 16000) #applies an fft algorithm to the data to collect their frequencies
    valid_buffer = (sample_frequency > 150) & (sample_frequency < 800) #creates a buffer so that low and high frequencies are ignored, preventing background frequencies from intefering
    valid_sample_magnitude = sample_magnitude[valid_buffer] #applies the buffer to sample_magnitude
    valid_sample_frequency = sample_frequency[valid_buffer] #applies the buffer to sample frequency
    frequency_peaks = valid_sample_frequency[valid_sample_magnitude > 30] #saves frequency values that have a corresponding magnitude greater than 30
    magnitude_peaks = valid_sample_magnitude[valid_sample_magnitude > 30] #saves magnitude values greater than 30
    if len(frequency_peaks) > 0: #if there are any peaks (i.e meaningful audio has been detected)
      main_freq = frequency_peaks[np.argmax(magnitude_peaks)] #determines the dominent frequency, which should always be the persons voice
    else:
      main_freq = None #if no peaks are detected, then there is no dominent frequency
    MIDI_note = (12 * np.log2(main_freq / 440.0)) + 69 #determines the MIDI note number of the given frequency. first divide by 440 to get a ratio between the detected frequency and A4
    #log2 to determine how many octavs away the note is from A4, times by 12 to covnert this into semitones away form A4. add 69 as that is the midi note number for A4, and therefore cenetrs it around A4
    MIDI_note = MIDI_note.astype(np.int16) #turns all values into integers so they can be used for indexing
    Audio.Hum_Detector.detect_hum(valid_sample_frequency, valid_sample_magnitude, main_freq) #calls the detect hum subroutine to check whether the sample was hummed
    var.note = note_names[MIDI_note % 12] #finds the note in letter notation
    var.recent_notes.append([MIDI_note, main_freq]) #adds the numerical note to the recent note list
    var.audio_start_time = time.monotonic() #sets audio start time
    if len(var.recent_notes) > 25:
      var.recent_notes.pop(0) #if the recent notes list is getting too long, remove the oldest item
  else:
    var.note = "-" #sets note to null
    var.humming = False #sets humming to false
    if singing == True:
      last_singing_time = time.monotonic() #gets the time and stores it
      singing = False
    if time.monotonic() - last_singing_time > 0.1:
      var.current_melody = np.array([], dtype = object)
      var.melody_lock = False
    if not len(var.recent_notes) == 0:
      var.recent_notes.pop(0)

threaded_audio = threading.Thread(target = collect_sample, daemon = True) #creates a thread so that the audio detection can run in parallel with the rest of the project
threaded_audio.start() #starts the thread