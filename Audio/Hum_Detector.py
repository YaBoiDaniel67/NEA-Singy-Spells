import Variables as var
import numpy as np

def detect_hum(frequency_list, magnitude_list, main_frequency):
    if main_frequency == None: #if there is no clear frequency
        var.humming = False #there is no humming
        return
    dominant_Mask = (frequency_list >= main_frequency - 30) & (frequency_list <= main_frequency + 30)  #creates a mask for the calculations so they only looks at values near the dominant frequency, blocking out background noises
    sum_frequency = np.sum(frequency_list[dominant_Mask] * magnitude_list[dominant_Mask]) #calculates the sum of weighted frequencies
    sum_magnitude = np.sum(magnitude_list[dominant_Mask]) #calculates the sum of magnitudes
    spectral_centroid = sum_frequency / (sum_magnitude + 1e-9) #calculates the weighted average, the spectral centroid

    F1_Mask = (300 <= frequency_list) & (800 >= frequency_list) #masks for F1 frequencies
    F2_Mask = (800 <= frequency_list) & (2500 >= frequency_list) #masks for F2 Frequencies
    dominant_energy = np.sum(magnitude_list[dominant_Mask]) 
    F1_energy = np.sum(magnitude_list[F1_Mask]) #calculates F1 peaks
    F2_energy = np.sum(magnitude_list[F2_Mask]) #calculates F2 peaks
    F1_ratio = F1_energy / (dominant_energy + 1e-9)
    F2_ratio = F2_energy / (dominant_energy + 1e-9)
    if spectral_centroid <= 450 and F1_ratio < 0.7 and F2_ratio < 0.5:
        var.humming = True
    else:
        var.humming = False