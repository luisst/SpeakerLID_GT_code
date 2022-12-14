import sys
import os
import glob

# To-do future: add regex to avoid re processing of csvs
# Do not process csv without timestamp
csv_folder = '/home/luis/Dropbox/SpeechFall2022/GT_speakerLID/G-C2L1P-Feb16-B-Shelby_q2_03-05/new_csvs'

folder_csv_list = sorted(glob.glob("{}/*.csv".format(csv_folder)))

folder_csv_cleared = [(x[:-29]+'.csv') for x in folder_csv_list]

# Verify no duplicates
set_folder_csv = set(folder_csv_cleared)
if len(set_folder_csv) != len(folder_csv_cleared):
   sys.exit("Found csv duplicates")

print(folder_csv_cleared)
# iterate over all audio sorted
for idx_csv, current_csv_path in enumerate(folder_csv_list):
    os.rename(current_csv_path, folder_csv_cleared[idx_csv])
