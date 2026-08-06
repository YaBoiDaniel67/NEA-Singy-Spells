import pyaudio
import threading
import numpy as np
from queue import Queue

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

audio_queue = Queue()
audio = pyaudio.PyAudio()
stream = audio.open(format = pyaudio.paInt16, #sets the data type as a 16 bit signed binray number
                     channels = 1, #sets the audio type as mono
                     rate = 16000, #sets the sample rate
                     input = True, #defines the stream as detecting sound from the mic
                     frames_per_buffer = 4096) #the amount of samples read in a given sample read

def collect_sample():
 while True:
  data = stream.read(4096) #reads 4096 samples from the stream
  audio_queue.put(data) #puts these samples in a queue

def transform_sample(input_queue):
 if not input_queue.empty(): #if the queue has sounds samples in it
  sample = input_queue.get() #get the set of samples and remove it from the queue

  sample = np.frombuffer(sample, dtype = np.int16) #converts the sample form binray numbers into decimal
  sample_magnitude = np.fft.rfft(sample)
  sample_magnitude = np.abs(sample_magnitude)
  sample_frequency = np.fft.rfftfreq(len(sample), 1.0 / 16000)
  valid = (sample_frequency > 150)
  valid_sample_strength = sample_magnitude[valid]
  valid_sample_freq = sample_frequency[valid]
  peaks = valid_sample_freq[valid_sample_strength > 30]
  peaks_mag = valid_sample_strength[valid_sample_strength > 30]
  if len(peaks) > 0:
   index = np.argmax(peaks_mag)
   main_freq = peaks[index]
  else:
   main_freq = None
  if 500 < np.mean(np.abs(sample)):
    numerical_note = (12 * np.log2(main_freq / 440.0)) + 69
    numerical_note = numerical_note.astype(np.int16)
    print(note_names[numerical_note % 12])


threaded_audio = threading.Thread(target = collect_sample, daemon = True)
threaded_audio.start()