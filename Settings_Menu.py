import pyaudio
import Button as Buttons

def find_mic_options(screenX, screenY, display, texture_dict):
    mic_list = []
    mic_dict = []
    audio = pyaudio.PyAudio()
    host_api = audio.get_default_host_api_info()["index"]
    for i in range(audio.get_device_count()):
        current_device = audio.get_device_info_by_index(i)
        if current_device["hostApi"] == host_api and current_device.get("maxInputChannels") > 0:
            mic_list.append(current_device.get("name"))
            mic_dict.append({current_device.get("name"): i})
    current_mics = []
    count = 0
    for i in range(len(mic_list)):
        current_mics.append(Buttons.Button(screenX, screenY, texture_dict["menu_button_background"], display, 0.5, 0.07 + (0.1 * count), 0.3, 0.05, mic_list[i]))
        count += 1
    audio.terminate()
    return current_mics, mic_dict

def display_mic_options(current_mics, mic_dict, mic_preference, texture_dict):
    for i in range(len(current_mics)):
        current_mics[i].draw_to_screen()
        if current_mics[i].check_pressed():
            current_mics[i].surface = texture_dict["menu_button_background_selected"]
            mic_preference = mic_dict[i][current_mics[i].text]
        else:
            if mic_preference != mic_dict[i][current_mics[i].text]:
                current_mics[i].surface = texture_dict["menu_button_background"]
            else:
                current_mics[i].surface = texture_dict["menu_button_background_selected"]
    return mic_preference
