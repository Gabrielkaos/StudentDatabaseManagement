import csv



with open("CSVDATA/to_be_added.csv","r") as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(row)