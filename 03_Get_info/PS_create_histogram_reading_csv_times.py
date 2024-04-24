from pathlib import Path
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# font = {'family' : 'normal',
#         'weight' : 'normal',
#         'size'   : 22}
# matplotlib.rc('font', **font)

def compute_histogram_bins(data, desired_bin_size):
    min_val = np.min(data)
    max_val = np.max(data)
    min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
    max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
    n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    return bins


def plot_histograms(input_list_all):
    bins = compute_histogram_bins(np.array(input_list_all), 250)     
    
    plt.figure()    
    n, bins, patches = plt.hist(x = input_list_all, bins=bins, color='#0504aa',
                                    alpha=0.7, rwidth=0.85)

    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Length in samples of all the audios')

    # plt.figure()    
    # n, bins, patches = plt.hist(x = input_list_all, bins=bins, color='g',
    #                                 alpha=0.7, rwidth=0.85, cumulative=True)

    # plt.grid(axis='y', alpha=0.75)
    # plt.xlabel('Value')
    # plt.ylabel('Frequency')
    # plt.title('CDF Length in samples of all the audios')

    plt.show()


txt_folder_pth = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO', 'Speech_vs_BackgroundNoise', 'Wenjing_GT', 'output_csv')
folder_txt_list = sorted(list(txt_folder_pth.glob('*.txt')))

total_lenght = []

for txt_pth in folder_txt_list:
    f = open(txt_pth, 'r')
    lines = f.readlines()
    f.close()

    for line in lines:
        video_name, start_time_txt, stop_time_txt, speaker_id = line.strip().split('\t')
        (hstart, mstart, sstart) = start_time_txt.split(':')
        start_time = float(hstart) * 3600 + float(mstart) * 60 + float(sstart)

        (hstop, mstop, sstop) = stop_time_txt.split(':')
        stop_time = float(hstop) * 3600 + float(mstop) * 60 + float(sstop)
        print(f'{video_name}')

        total_lenght.append(stop_time-start_time)

# print(total_lenght)
# plot_histograms(total_lenght)

bins = compute_histogram_bins(np.array(total_lenght), 3)     

plt.figure()    
n, bins, patches = plt.hist(x = total_lenght, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)

plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Length in samples of all the audios')
plt.show()