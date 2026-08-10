import csv

def load_csv_for_reading(csv_file_name):
    values = {}
    with open(csv_file_name, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for i, j, k in reader:
            i = int(i)
            if i not in values:
                values[i] = []
            values[i].append([int(j), float(k)])
        return(values)