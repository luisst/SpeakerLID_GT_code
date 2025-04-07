import pathlib
from utilities_functions import calculate_duration_in_folder

# Example usage:
directory_path = pathlib.Path.cwd()
current_time = calculate_duration_in_folder(directory_path, wav_flag = True)

total_min = current_time/60
total_hours = total_min/60

print(f'The total seconds in this folder is: {current_time:.2f}')
print(f'In minutes: {total_min:.2f} \t In hours: {total_hours:.2f}')

