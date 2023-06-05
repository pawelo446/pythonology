import csv
import random

def generate_csv_data(file_name, num_rows):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for _ in range(num_rows):
            row = [random.randint(1, 100) for _ in range(5)]  # Generate 5 random numbers per row
            writer.writerow(row)

# Usage example:
generate_csv_data('data.csv', 10)  # Generate a CSV file with 10 rows
