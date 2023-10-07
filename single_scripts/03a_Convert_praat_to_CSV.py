from pathlib import Path
import sys
from utilities_functions import check_folder_for_process
from scripts_functions import simplify_praat, convert_to_csv
from clips_samples_functions import convert_praat_2_csv



if __name__=="__main__":
    #Iterate all csv files in folder
    base_video_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST','G-C2L1P-Apr12-A-Allan_TEST')

    folder_pth = base_video_pth.joinpath('praat_files')
    final_csv_pth = base_video_pth.joinpath('final_csv')

    convert_praat_2_csv(folder_pth, final_csv_pth, 
                        tag_from_praat = 'done', tag_after_finished = 'ready')
