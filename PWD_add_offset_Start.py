import csv
from pathlib import Path

def add_to_columns(file_path):
    # Open the CSV file for reading
    with open(file_path, 'r', newline='') as file:

        # Create a CSV reader object
        reader = csv.reader(file, delimiter='\t')

        # Create a list to hold the updated rows
        updated_rows = []

        # Loop through each row in the file
        for row in reader:

            # Get the values from the 2nd and 3rd columns
            col2 = float(row[1])
            # col3 = float(row[2])

            # Add 0.05 to each value
            col2 += 0.05
            # col3 += 0.05

            # Update the row with the new values
            row[1] = str(col2)
            # row[2] = str(col3)

            # Add the updated row to the list
            updated_rows.append(row)

    # Write the updated rows back to the file
    with open(file_path, 'w', newline='') as file:

        # Create a CSV writer object
        writer = csv.writer(file, delimiter='\t')

        # Write each row to the file
        for row in updated_rows:
            writer.writerow(row)

# Get the current directory
current_dir = Path.cwd()

# Loop through all files in the current directory
for file_path in current_dir.glob("*.csv"):
    # Apply the function to CSV files only
    if file_path.suffix == ".csv":
        add_to_columns(file_path)
