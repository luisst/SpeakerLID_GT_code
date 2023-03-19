from pathlib import Path
import math
import sys
from itertools import combinations
import random

from utilities_functions import check_folder_for_process

def convert_naming(current_wav_name):

    speaker_ID = current_wav_name.split('_')[-2]
    return speaker_ID + '/' + current_wav_name

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','Interviews_output','Speakers_folder')

all_wavs_pth_list = sorted(list(root_dir.rglob('*.wav')))

output_pairs_aolme_pth = root_dir.joinpath('test_pair_aolme_interviews.txt') 

new_file = open(output_pairs_aolme_pth, "w")

speakers_dict = {}

for current_wav_pth in all_wavs_pth_list:
    speaker_ID = current_wav_pth.name.split('_')[-2]
    print(speaker_ID)

    if speaker_ID not in speakers_dict:
        speakers_dict[speaker_ID] = [current_wav_pth.name]
    else:
        speakers_dict[speaker_ID].append(current_wav_pth.name)

for current_speaker, current_speaker_list in speakers_dict.items():
    print(current_speaker)
    full_comb_list = list(combinations(current_speaker_list, 2))
    entries_to_add = min(len(current_speaker_list),len(full_comb_list))
    entries_to_add = min(math.floor(len(all_wavs_pth_list)/2), entries_to_add)

    comb_list = []
    while len(comb_list) < entries_to_add:
        candidate_pair = random.choice(full_comb_list)

        if candidate_pair not in comb_list:
            comb_list.append(candidate_pair)
        # else:
        #     print(f'Tried pair: {candidate_pair}')

    rand_audios = []
    # Create a list with all other speakers
    all_candidates_list = []
    for key in speakers_dict.keys():
        if key != current_speaker:
            all_candidates_list.extend(speakers_dict[key])
    
    print(f'This is my list of all candidates: {all_candidates_list}')

    while len(rand_audios) < entries_to_add:
        candidate_audio = random.choice(all_candidates_list)
        all_candidates_list.remove(candidate_audio)

        if candidate_audio not in rand_audios:
            rand_audios.append(candidate_audio)
        else:
            print(f'Tried name: {candidate_audio}')

    print(f'comb_list: {len(comb_list)}\t rand_audios: {len(rand_audios)}') 

    for idx in range(0, len(rand_audios)):
        current_pos1 = convert_naming(comb_list[idx][0])
        current_pos2 = convert_naming(comb_list[idx][1])

        new_file.write(f'1 {current_pos1} {current_pos2}\n') 
        inter_idx = int(idx%2)
        print(f'This is my index: {inter_idx}')

        current_neg1 = convert_naming(comb_list[inter_idx][0])
        current_neg2 = convert_naming(rand_audios[idx])

        new_file.write(f'0 {current_neg1} {current_neg2}\n') 

new_file.close()