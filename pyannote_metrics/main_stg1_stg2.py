
import sys
from pathlib import Path

from pyannote.metrics.diarization import DiarizationCoverage
from pyannote.metrics.diarization import DiarizationPurity
from pyannote.metrics.detection import DetectionAccuracy, DetectionErrorRate
from pyannote.core import Annotation, Segment

from utilities_functions import matching_basename_pathlib_gt_pred


def vad_format(current_transcript_pth):
    # Src	Lang    StartTime	EndTime
    # s0    Eng 	3.93	    5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    reference = Annotation()
    for line in lines:
        Speaker, Lang, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return reference


def stg1_format(current_transcript_pth):
    # Src	StartTime	EndTime
    # s0s0	3.93	5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]
    lines.pop(0)

    reference = Annotation()
    for line in lines:
        SpeakerLang, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return reference


def select_method(pred_method):
    if pred_method == 'stg':
        return stg1_format


def vad_calculation(pred_method, current_matches ):

    if len(current_matches) == 0:
        print(f'ERROR: no matches found! in {pred_method}')
        return 0
    
    func_pred = select_method(pred_method)

    all_vad_acc = []


    for current_gt_pth, current_pred_pth in current_matches:
        current_reference = vad_format(current_gt_pth)
        current_hypothesis = func_pred(current_pred_pth)

        # vad_pyannote = DetectionAccuracy()
        vad_pyannote = DetectionErrorRate()

        current_DER = vad_pyannote(current_reference, current_hypothesis)
        print(f'DER: {current_DER}')

        all_vad_acc.append(current_DER)
    
    return sum(all_vad_acc) / len(all_vad_acc)


# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection',
                                '02_Selected_clips','G-C2L1P-Feb16-B-Shelby_q2_03-05')

# Load GT list:
stg2_pth = root_dir.joinpath('final_csv')


### List of all available models:

# Audiotok: 
stg1_pth = root_dir.joinpath('csv_from_webapp')

stg_matches = matching_basename_pathlib_gt_pred(stg2_pth, stg1_pth, 
        gt_suffix_added='praat_ready', pred_suffix_added='',
        gt_ext = 'csv', pred_ext = 'csv', verbose=True)

stg1_acc = vad_calculation('stg', stg_matches)
print(f'stg1_acc: {(stg1_acc):.2f}')

