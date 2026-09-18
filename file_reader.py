import csv #imports csv

def extract_game_melodies(file_name):
    values = {} #sets values as an empty dictionary
    with open(file_name, "r") as file: #opens the csv file
        reader = csv.reader(file) #saves reader to a variable
        next(reader) #skips the top row as that is not info, just column meanings/names
        for i, j, k in reader:
            i = int(i) #ensures the melody_ID is an int
            if i not in values: #if this ID has not yet been added
                values[i] = [] #creates an empty list at i
            values[i].append([int(j), float(k)]) #adds to this list the note and time it should be held for
        return values #returns values

def extract_map(map_num):
    map = []
    with open("Graphics/Maps.txt", "r") as file:
        current_map_id = 0
        current_line_num = 0
        lines = file.readlines()
        for row in lines:
            row = row.strip()
            if row == "":
                current_map_id += 1
            if current_map_id == map_num:
                break
            current_line_num += 1
        while lines[current_line_num] != "\n":
            current_row = list(lines[current_line_num].strip())
            for i in range(len(current_row)):
                current_row[i] = int(current_row[i])
            map.append(current_row)
            current_line_num += 1
    return map