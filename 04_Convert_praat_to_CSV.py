from pathlib import Path
import sys
from UtilsTranscripts import simplify_praat, convert_to_csv, check_folder_for_process

#Iterate all csv files in folder
base_video_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST','G-C2L1P-Apr12-A-Allan_TEST')

folder_pth = base_video_pth.joinpath('praat_files')
final_csv_pth = base_video_pth.joinpath('final_csv')

tag_from_praat = 'done'
tag_after_finished = 'ready'

if check_folder_for_process(final_csv_pth):
    for praat_pth in folder_pth.glob( f'*_{tag_from_praat}.txt' ):
        print(f'\tNow processing: {praat_pth}\n')
        conrrected_praat_name = praat_pth.stem

        new_transcript_name = conrrected_praat_name.split('.')[0] + f'_{tag_after_finished}.csv'
        simplified_transcr_path = final_csv_pth.joinpath(new_transcript_name)

        simplify_praat(praat_pth, simplified_transcr_path)

        convert_to_csv(simplified_transcr_path, simplified_transcr_path)

        


        

