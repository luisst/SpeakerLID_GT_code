import pickle
import sys
from pathlib import Path
from mycolorpy import colorlist as mcp

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# font = {'family' : 'normal',
#         'weight' : 'normal',
#         'size'   : 22}
# matplotlib.rc('font', **font)

from utilities_functions import calculate_duration_in_folder


root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','Interviews_output','Speakers_folder')

extract_info_flag = False

if extract_info_flag:
    speakers_dict = {}

    # Extract Number of audios, Total duration, and Duration of each audio
    for current_path in Path(root_dir).iterdir():
        if current_path.is_file():
            print(f'This is a file skipped: {current_path.name}')

        if current_path.is_dir():
            print(current_path)
            speaker_ID = current_path.name

            # Go inside the folder and grab time
            list_lengths, total_time_folder = calculate_duration_in_folder(current_path, wav_flag = True, return_list = True)

            # Go inside folder and get number of speakers
            audios_list_in_folder = sorted(list(current_path.glob('*.wav')))
            number_audios_in_folder = len(audios_list_in_folder)

            # Revise speaker_ID doesn't exist
            if speaker_ID not in speakers_dict.keys():
                speakers_dict[speaker_ID] = [number_audios_in_folder, total_time_folder, list_lengths]
            else:
                sys.error(f'Speaker ID {speaker_ID} already exist!!')

    # Save as pickle file
    with open(f'speakers_info_{root_dir.name}.pickle', 'wb') as handle:
        pickle.dump(speakers_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Load the info
with open(f'speakers_info_{root_dir.name}.pickle', 'rb') as handle:
    speakers_dict = pickle.load(handle)


def compute_histogram_bins(data, desired_bin_size):
    min_val = np.min(data)
    max_val = np.max(data)
    print(f'Min val {min_val} | max val {max_val}')
    min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
    max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
    n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    return bins


def plot_histograms(input_list_all, desired_bin_size, cdf_flag = False):
    bins = compute_histogram_bins(np.array(input_list_all), desired_bin_size)     
    
    plt.figure()    
    n, bins, patches = plt.hist(x = input_list_all, bins=bins, color='#0504aa',
                                    alpha=0.7, rwidth=0.85)

    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Length in samples of all the audios')

    if cdf_flag:
        plt.figure()    
        n, bins, patches = plt.hist(x = input_list_all, bins=bins, color='g',
                                        alpha=0.7, rwidth=0.85, cumulative=True)

        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title('CDF Length in samples of all the audios')

    plt.show()

speakers_keys = list(speakers_dict.keys())
trial_lengths = speakers_dict[speakers_keys[0]][2]

# plot_histograms(trial_lengths, 1, cdf_flag=True)

number_audios_list = []
labels_list = []
seconds_audios_list = []
for current_key in speakers_dict.keys():
    seconds_audios_list.append(speakers_dict[current_key][1])
    number_audios_list.append(speakers_dict[current_key][0])
    labels_list.append(current_key)

labels_seconds = [f'{s:0.1f} sec' for s in seconds_audios_list]
labels_numbers = [f'#{s}' for s in number_audios_list]

color1=mcp.gen_color(cmap="viridis",n=len(seconds_audios_list))
# color2=mcp.gen_color(cmap="cividis",n=len(number_audios_list))
color2=mcp.gen_color(cmap="viridis",n=len(number_audios_list))

fig1, (ax1, ax2) = plt.subplots(1,2)
fig1.suptitle(f'{root_dir.parent.name}')
ax1.pie(np.array(number_audios_list), labels=labels_list, autopct='%1.1f%%',
        startangle=90, colors=color1)
ax1.axis('equal')
ax1.legend(loc='upper left', labels = labels_numbers)   
ax1.set_title('Number of Audios per Speaker')
 
ax2.pie(np.array(seconds_audios_list), labels=labels_list, autopct='%1.1f%%',
        startangle=90, colors=color2)
ax2.axis('equal')
ax2.legend(loc='upper right', labels = labels_seconds)   
ax2.set_title('Seconds per Speaker')
plt.show() 