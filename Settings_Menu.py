import pyaudio
import Button as Buttons

def find_mic_options(screenX, screenY, display, texture_dict):
    mic_list = []
    mic_dict = []
    audio = pyaudio.PyAudio() #opens an instance of pyaudio
    host_api = audio.get_default_host_api_info()["index"] #gets the index of the devices current host API
    for i in range(audio.get_device_count()): #for all the devices currently available in this pyaudio instance
        current_device = audio.get_device_info_by_index(i) #saves the current device being worked with to a variable for ease
        if current_device["hostApi"] == host_api and current_device.get("maxInputChannels") > 0: #if this devices host API is the devices, and it has any input channels then it is a valid mic
            mic_list.append(current_device.get("name")) #adds the name of this device to mic list
            mic_dict.append({current_device.get("name"): i}) #creates a dict linking this mic name and the index where this mic can be accessed
    current_mics = []
    for i in range(len(mic_list)): #for all the mics found
        current_mics.append(Buttons.Button(screenX, screenY, texture_dict["menu_button_background"], display, 0.5, 0.07 + (0.1 * i), 0.3, 0.05, mic_list[i])) #creates a button of this mic, increasing in y value as the for loop increases
    audio.terminate() #terminates this instance of pyaduio
    return current_mics, mic_dict

def display_mic_options(current_mics, mic_dict, mic_preference, texture_dict):
    for i in range(len(current_mics)): #for all the current mics
        current_mics[i].draw_to_screen() #draws it to screen
        if current_mics[i].check_pressed(): #if it has been pressed
            current_mics[i].surface = texture_dict["menu_button_background_selected"] #changes the buttons surface to show it as selected
            mic_preference = mic_dict[i][current_mics[i].text] #sets this as mic preference
        else:
            if mic_preference != mic_dict[i][current_mics[i].text]: #if this mic is not the preferred one
                current_mics[i].surface = texture_dict["menu_button_background"] #sets its background to unselected
            else:
                current_mics[i].surface = texture_dict["menu_button_background_selected"] #if this mic is preferred, sets its background to selected
    return mic_preference #returns the preferred mic
