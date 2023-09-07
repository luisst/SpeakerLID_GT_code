from pathlib import Path
import csv

folder_path = Path.cwd()  # Replace with the path to your folder

# Iterate over all CSV files in the folder
for file_path in folder_path.glob("*.csv"):
    # Read the contents of the CSV file
    with open(file_path, "r") as file:
        reader = csv.reader(file, delimiter="\t")
        lines = list(reader)

    # Modify the first column values
    for i in range(len(lines)):
        if lines[i][0] == "S1":
            lines[i][0] = "S3"
        elif lines[i][0] == "S3":
            lines[i][0] = "S1"

    # Overwrite the file with the modified contents
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(lines)

    print(f"File '{file_path.name}' processed and overwritten.")