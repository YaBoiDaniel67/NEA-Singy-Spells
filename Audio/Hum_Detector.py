import numpy as np

def detect_hum(frequency_list, magnitude_list, main_frequency):
    if main_frequency == None: #if there is no clear frequency
        humming = False #there is no humming
        return
    dominant_Mask = (frequency_list >= main_frequency - 30) & (frequency_list <= main_frequency + 30)  #creates a mask for the calculations so they only look at values near the dominant frequency, blocking out background noises
    sum_frequency = np.sum(frequency_list[dominant_Mask] * magnitude_list[dominant_Mask]) #calculates the sum of weighted frequencies
    sum_magnitude = np.sum(magnitude_list[dominant_Mask]) #calculates the sum of magnitudes
    spectral_centroid = sum_frequency / (sum_magnitude + 1e-6) #calculates the weighted average, the spectral centroid
    F1_Mask = (300 <= frequency_list) & (800 >= frequency_list) #masks for F1 frequencies
    F2_Mask = (800 <= frequency_list) & (2500 >= frequency_list) #masks for F2 Frequencies
    dominant_sound= np.sum(magnitude_list[dominant_Mask]) 
    F1_energy = np.sum(magnitude_list[F1_Mask]) #calculates the sum of the magnitude of F1 values
    F2_energy = np.sum(magnitude_list[F2_Mask]) #calculates the sum of the magnitude of F2 values
    F1_ratio = F1_energy / (dominant_sound + 1e-6) #calculates F1 ratio, in relation to dominant sound
    F2_ratio = F2_energy / (dominant_sound + 1e-6) #calculates F2 ratio, in relation to dominant sound
    if spectral_centroid <= 450 and F1_ratio < 0.7 and F2_ratio < 0.5: #if all ccomputed values suggest humming
        humming = True
    else:
        humming = False
    return humming