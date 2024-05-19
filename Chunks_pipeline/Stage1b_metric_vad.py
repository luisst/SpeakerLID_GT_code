
from pathlib import Path
import pandas as pd
import os
import argparse
from pyannote.metrics.detection import DetectionAccuracy, DetectionErrorRate, DetectionPrecision, DetectionRecall
from pyannote.core import Segment
import pprint

from utilities_pyannote_methods_formats import vad_format, select_method
from utilities_functions import find_audio_duration
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred

from utilities_entropy import create_histogram
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)



def vad_calculation(pred_method,
                    current_matches,
                    audios_folder,
                    suffix_added,
                    current_log,
                    verbose = False):

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

        log_print(f'\n\n\t\t{pred_method}\t{current_gt_pth.stem} - {total_speech:.2f}s / {current_audio_duration:.2f}s', file=current_log)
        log_print(f'\tAcc: {accuracy_val:.2f}%\tMissed_speech: {missed_speech_rate}% ({missed_speech_val:.1f}s)\tFalse_speech: {false_speech_rate:.1f}% ({false_speech_val:.1f}s)\t|\tPrec: {precision_rate_val:.1f}%\tRecall: {recall_rate_val:.1f}%', file=current_log)

    # Calculate the average of all the metrics
    all_vad_metric = pd.DataFrame(all_vad_metric)
    all_vad_metric = all_vad_metric.mean()

    log_print(f"\n\n{pred_method}\tAverage Metrics Values:", file=current_log)
    log_print(f"Acc: {all_vad_metric['accuracy']:.2f}%\tMissed_speech: {all_vad_metric['missed_speech']:.1f}%\tFalse_speech: {all_vad_metric['false_speech']:.1f}%\tPrec: {all_vad_metric['precision']:.1f}%\tRecall: {all_vad_metric['recall']:.1f}%\n", file=current_log)
    log_print(f'\n\n\n', file=current_log)

    return all_vad_metric


def log_print(obj, pprint_flag = False, file='output_console.txt'):
        if pprint_flag:
                message = pprint.pformat(obj)
        else:
                message = str(obj) 

        print(message)
        with open(file, 'a') as f:
                f.write(message + '\n')


def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


# Root of all results
root_dir_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Proposal_runs','TestAO-Irma', )
audios_folder_ex = root_dir_ex.joinpath('input_wavs') 
GT_csv_folder_ex = root_dir_ex.joinpath('GT_final')
csv_pred_folder_ex = root_dir_ex.joinpath('STG_1', 'STG1_SHAS', 'shas_output_csv')
metric_output_folder_ex = root_dir_ex.joinpath('STG_1', 'STG1_SHAS','metrics')

### List of all available models:
parser = argparse.ArgumentParser()

parser.add_argument('--csv_pred_folder', type=valid_path, default=csv_pred_folder_ex, help='Folder with predicted VAD CSVs')
parser.add_argument('--GT_csv_folder', type=valid_path, default=GT_csv_folder_ex, help='Folder with the GT CSVs')
parser.add_argument('--audios_folder', type=valid_path, default=audios_folder_ex, help='Initial WAVs folder path')
parser.add_argument('--metric_output_folder', type=valid_path, default=metric_output_folder_ex, help='Folder to save the metrics log CSVs')

parser.add_argument('--pred_suffix', default='', help='Suffix added to the VAD files')
parser.add_argument('--pred_extensions', default='txt', help='extension of the VAD files')
parser.add_argument('--method_name', default='default_VAD_method', help='Method name, SHAS')
parser.add_argument('--run_name', default='default_name', help='Run ID name')


args = parser.parse_args()

csv_pred_folder = args.csv_pred_folder
GT_csv_folder = args.GT_csv_folder
audios_folder = args.audios_folder
metric_output_folder = args.metric_output_folder
pred_suffix_added = args.pred_suffix
pred_ext = args.pred_extensions
method_type = args.method_name
run_name = args.run_name

method_type = method_type.lower()
verbose = True


current_date_time = pd.to_datetime('today').strftime('%Y-%m-%d_%H-%M')
mylog = str(metric_output_folder.joinpath(f'VAD_metrics_{run_name}_{current_date_time}.txt'))

log_print(f'Running {method_type} method with {run_name} run name\n')

# SHAS
if method_type == 'shas':
    shas_matches = matching_basename_pathlib_gt_pred(GT_csv_folder, csv_pred_folder, 
            gt_suffix_added='GT', pred_suffix_added=pred_suffix_added,
            gt_ext = 'csv', pred_ext = pred_ext)

    shas_all_vad_metric =  vad_calculation(method_type,
                                           shas_matches,
                                           audios_folder,
                                           'GT',
                                           mylog,
                                           verbose = verbose)

    create_histogram(metric_output_folder,
                     method_type,
                     run_name,
                     shas_matches,
                     cdf_flag=True)
else:
    print(f'ERROR: method_type: {method_type} not found!')

