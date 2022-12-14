import UtilsTranscripts as gt
    # # Check if output audios are present
    # if check_folder_for_process(GT_audio_output_folder):

#############       First step: Divide into selections + webapp      ##############

#############       Second step: Read CSV -> Praat      ##############

#############       Third step: Praat -> audio samples      ##############
# Give the audios + csv folder
current_folder_videos = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST', 'G-C2L1P-Apr12-A-Allan_TEST')
current_folder_csv = current_folder_videos.joinpath('final_csv')

GT_audio_output_folder = current_folder_videos.joinpath('GT_audio_output_folder')

gt.gen_audio_samples(current_folder_videos,
current_folder_csv,
GT_audio_output_folder,
sr = 16000,
praat_extension = '_' + 'praat_done_ready'
tony_flag = True,
)