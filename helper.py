# module contains miscellaneous functions
import csv

class helper():
    # function parses a string and converts to appropriate type
    @staticmethod
    def convert(value):
        types = [int,float,str] # order needs to be this way
        if value == '':
            return None
        # CSV booleans arrive as the literal text TRUE/FALSE, which would
        # otherwise be stored (and later read back) as a truthy non-empty
        # string in both cases -- normalize to 1/0 first.
        if value.strip().upper() == 'TRUE':
            return 1
        if value.strip().upper() == 'FALSE':
            return 0
        for t in types:
            try:
                return t(value)
            except:
                pass

    # function reads file path to clean up data file
    # every seed CSV in this project has a header row as line 1 (column
    # names), so it's always skipped rather than inserted as data.
    # Uses the csv module (not a naive split(",")) so quoted fields
    # containing commas -- e.g. drink descriptions -- parse correctly.
    @staticmethod
    def data_cleaner(path):
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)[1:]
        data_cleaned = []
        for row in rows:
            if not any(cell.strip() for cell in row):
                continue
            row = [helper.convert(i) for i in row]
            data_cleaned.append(tuple(row))
        return data_cleaned

    # function checks for user input given a list of choices
    @staticmethod
    def get_choice(lst):
        choice = input("Enter choice number: ")
        while choice.isdigit() == False:
            print("Incorrect option. Try again")
            choice = input("Enter choice number: ")

        while int(choice) not in lst:
            print("Incorrect option. Try again")
            choice = input("Enter choice number: ")
        return int(choice)

    # function prints a list of strings nicely
    @staticmethod
    def pretty_print(lst):
        print("Results..\n")
        for i in lst:
            print(i)
        print("")
