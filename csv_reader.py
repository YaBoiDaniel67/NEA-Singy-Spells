import csv #imports csv

def load_csv_for_reading(csv_file_name):
    values = {} #sets values as an empty dictionary
    with open(csv_file_name, "r") as file: #opens the csv file
        reader = csv.reader(file) #saves reader to a variable
        next(reader) #skips the top row as that is not info, just column meanings/names
        for i, j, k in reader:
            i = int(i) #ensures the melody_ID is an int
            if i not in values: #if this ID has not yet been added
                values[i] = [] #creates an empty list at i
            values[i].append([int(j), float(k)]) #adds to this list the note and time it should be held for
        return values #returns values