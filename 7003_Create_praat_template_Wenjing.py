from pathlib import Path
import sys
import clips_samples_functions as gt

from utilities_functions import check_folder_for_process, calculate_duration_in_folder

speaker_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','Extra_output','Speakers_folder_TalkvsNoTalk','Herminio10P')

# output_root_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','Extra_output')
# output_split_speakers_folder = output_root_folder.joinpath('Groups_Feb23')
output_split_speakers_folder = speaker_folder

# if not(check_folder_for_process(output_split_speakers_folder)):
#     sys.exit('goodbye')

# Go inside the folder and grab time
list_names, list_lengths, total_time_folder = calculate_duration_in_folder(speaker_folder,
                                                                wav_flag = True,
                                                                return_list = True,
                                                            return_names = True)

for current_name, total_time in list(zip(list_names, list_lengths)):

    new_transcr_path = output_split_speakers_folder.joinpath(current_name.split('.')[0] + '.txt')
    new_file = open(new_transcr_path, "w")

    template = f'"ooTextFile"\n"TextGrid"\n0 {total_time}\n<exists>\n5 tiers\n'
    template += f'"IntervalTier" "S0"\n0 {total_time}\n1 interval coming\n0 {total_time} ""\n'
    template += f'"IntervalTier" "S1"\n0 {total_time}\n1 interval coming\n0 {total_time} ""\n'
    template += f'"IntervalTier" "S2"\n0 {total_time}\n1 interval coming\n0 {total_time} ""\n'
    template += f'"IntervalTier" "S3"\n0 {total_time}\n1 interval coming\n0 {total_time} ""\n'
    template += f'"IntervalTier" "S4"\n0 {total_time}\n1 interval coming\n0 {total_time} ""\n'

    new_file.write(template)

    new_file.close()
