import Variables as var

def detect_hum(frequency_list, magnitude_list, main_frequency):
    dominant_Mask = (frequency_list >= main_frequency - 50) & (frequency_list <= main_frequency + 50)  #creates a mask for the calculations so they only looks at values near the dominant frequency, blocking out background noises
    sum_frequency = sum(frequency_list[dominant_Mask] * magnitude_list[dominant_Mask]) #calculates the sum of weighted frequencies
    sum_magnitude = sum(magnitude_list[dominant_Mask]) #calculates the sum of magnitudes
    spectral_centroid = sum_frequency / sum_magnitude #calculates the weighted average, the spectral centroid

    F1_Mask = (300 <= frequency_list) & (800 >= frequency_list) #masks for F1 frequencies
    F2_Mask = (800 <= frequency_list) & (2500 >= frequency_list) #masks for F2 Frequencies
    dominant_energy = sum(magnitude_list[dominant_Mask]) 
    F1_energy = sum(magnitude_list[F1_Mask])
    F2_energy = sum(magnitude_list[F2_Mask])
    F1_ratio = F1_energy / dominant_energy
    F2_ratio = F2_energy / dominant_energy
    if spectral_centroid <= 300 and F1_ratio < 2 and F2_ratio < 2:
        var.humming = True
    else:
        var.humming = False