from pathlib import Path
import pandas as pd

from pyannote.metrics.detection import DetectionAccuracy, DetectionErrorRate, DetectionPrecision, DetectionRecall
from pyannote.core import Segment

from utilities_pyannote_methods_formats import vad_format, select_method
from utilities_functions import find_audio_duration
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)



def vad_calculation(pred_method, current_matches, audios_folder, suffix_added, verbose = False):

    if len(current_matches) == 0:
        print(f'ERROR: no matches found! in {pred_method}')
        return 0
    
    func_pred = select_method(pred_method)

    all_vad_metric = []
    for current_gt_pth, current_pred_pth in current_matches:

        # Name of the current gt file
        current_gt_name = current_gt_pth.stem

        current_audio_duration = find_audio_duration(current_gt_pth, audios_folder, suffix_added)

        ground_truth = vad_format(current_gt_pth)
        hypothesis = func_pred(current_pred_pth)

        # Calculate metrics
        accuracy = DetectionAccuracy()
        error_rate = DetectionErrorRate()
        precision_rate = DetectionPrecision()
        recall_rate = DetectionRecall()

        # Calculate metrics
        accuracy_val = accuracy(ground_truth, hypothesis, uem=Segment(0, current_audio_duration))
        error_rate_dict = error_rate.compute_components(ground_truth, hypothesis, uem=Segment(0, current_audio_duration))
        missed_speech_val = error_rate_dict['miss']
        false_speech_val = error_rate_dict['false alarm']
        error_rate_val = error_rate(ground_truth, hypothesis, uem=Segment(0, current_audio_duration))*100
        precision_rate_val = precision_rate(ground_truth, hypothesis, uem=Segment(0, current_audio_duration))*100
        recall_rate_val = recall_rate(ground_truth, hypothesis, uem=Segment(0, current_audio_duration))*100

        total_speech = error_rate_dict['total']
        # missed_speech_rate = round((missed_speech_val / error_rate_dict['total'])*100, 1)
        # false_speech_rate = round((false_speech_val / error_rate_dict['total'])*100, 1)


        missed_speech_rate = round((missed_speech_val / current_audio_duration)*100, 1)
        false_speech_rate = round((false_speech_val / current_audio_duration)*100, 1)
        

        # Append current metrics to the lists
        all_vad_metric.append({
            'accuracy': accuracy_val,
            'error_rate': error_rate_val,
            'missed_speech': missed_speech_rate,
            'false_speech': false_speech_rate,
            'precision': precision_rate_val,
            'recall': recall_rate_val
        })

        print(f'\n\n\t\t{pred_method}\t{current_gt_pth.stem} - {total_speech:.2f}s / {current_audio_duration:.2f}s')
        print(f'\tAcc: {accuracy_val:.2f}%\tMissed_speech: {missed_speech_rate}% ({missed_speech_val:.1f}s)\tFalse_speech: {false_speech_rate:.1f}% ({false_speech_val:.1f}s)\t|\tPrec: {precision_rate_val:.1f}%\tRecall: {recall_rate_val:.1f}%')

    # Calculate the average of all the metrics
    all_vad_metric = pd.DataFrame(all_vad_metric)
    all_vad_metric = all_vad_metric.mean()

    print(f"\n\n{pred_method}\tAverage Metrics Values:")
    print(f"Acc: {all_vad_metric['accuracy']:.2f}%\tMissed_speech: {all_vad_metric['missed_speech']:.1f}%\tFalse_speech: {all_vad_metric['false_speech']:.1f}%\tPrec: {all_vad_metric['precision']:.1f}%\tRecall: {all_vad_metric['recall']:.1f}%\n")
    print(f'\n\n\n')

    return all_vad_metric

# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD','All_results')
audios_folder = root_dir.parent.joinpath('WAV_FILES') 

# Load GT list:
GT_pth = root_dir.parent.joinpath('GT_csv')
verbose = True

### List of all available models:

# SHAS
shas_pth = root_dir.joinpath('shas','final_csv')

shas_matches = matching_basename_pathlib_gt_pred(GT_pth, shas_pth, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')

shas_all_vad_metric =  vad_calculation('shas', shas_matches, audios_folder, 'GT', verbose = verbose)


# Whisper openAI
whisper_pth = root_dir.joinpath('whisper','final_csv')

whisper_matches = matching_basename_pathlib_gt_pred(GT_pth, whisper_pth, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')

whisper_all_vad_metric =  vad_calculation('whisper', whisper_matches, audios_folder, 'GT', verbose = verbose)

# azure 
azure_pth = root_dir.joinpath('azure','final_csv_v31')

azure_matches = matching_basename_pathlib_gt_pred(GT_pth, azure_pth, 
        gt_suffix_added='GT', 
        gt_ext = 'csv', pred_ext = 'txt')

azure_all_vad_metric =  vad_calculation('azure', azure_matches, audios_folder, 'GT', verbose = verbose)

# silero 
silero_pth = root_dir.joinpath('silero')

silero_matches = matching_basename_pathlib_gt_pred(GT_pth, silero_pth, 
        gt_suffix_added='GT', pred_suffix_added='silero', 
        gt_ext = 'csv', pred_ext = 'csv')

silero_all_vad_metric =  vad_calculation('silero', silero_matches, audios_folder, 'GT', verbose = verbose)