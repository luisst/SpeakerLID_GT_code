
import sys
from pathlib import Path

from pyannote.metrics.diarization import DiarizationCoverage
from pyannote.metrics.diarization import DiarizationPurity
from pyannote.metrics.detection import DetectionAccuracy, DetectionErrorRate

from pyannote.metrics.detection import DetectionPrecision, DetectionRecall
from pyannote.core import Annotation, Segment

from utilities_functions import matching_basename_pathlib_gt_pred


def vad_format(current_transcript_pth):
    # Src	Lang    StartTime	EndTime
    # s0    Eng 	3.93	    5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    reference = Annotation()
    for line in lines:
        Speaker, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return reference


def vad_calculation(current_matches):

    all_vad_acc = []
    all_vad_recall = []
    all_vad_prec = []

    for current_gt_pth, current_pred_pth in current_matches:
        current_reference = vad_format(current_gt_pth)
        current_hypothesis = vad_format(current_pred_pth)

        # vad_pyannote = DetectionAccuracy()
        vad_pyannote = DetectionErrorRate()
        prec_pyannote = DetectionPrecision()
        recall_pyannote = DetectionRecall()

        current_DER = vad_pyannote(current_reference, current_hypothesis)
        current_recall = prec_pyannote(current_reference, current_hypothesis)
        current_prec = recall_pyannote(current_reference, current_hypothesis)
        print(f'\t acc: {(current_DER):.2f} \t prec: {(current_prec):.2f} \t recall: {(current_recall):.2f}')

        all_vad_acc.append(current_DER)
        all_vad_recall.append(current_recall)
        all_vad_prec.append(current_prec)

    result_acc = sum(all_vad_acc) / len(all_vad_acc)
    result_recall = sum(all_vad_recall) / len(all_vad_recall)
    result_prec = sum(all_vad_prec) / len(all_vad_prec)
    
    return result_acc, result_prec, result_recall 


# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TTS_minitest')

# Load GT list:
GT_pth = root_dir.joinpath('GT')
pred_pth = root_dir.joinpath('inference')


shas_matches = matching_basename_pathlib_gt_pred(GT_pth, pred_pth, 
        gt_suffix_added='', pred_suffix_added='',
        gt_ext = 'csv', pred_ext = 'csv', verbose=True)

shas_acc, shas_prec, shas_recall = vad_calculation(shas_matches)
print(f'\n\nshas_acc: {(shas_acc):.2f} \t shas_prec: {(shas_prec):.2f} \t shas_recall: {(shas_recall):.2f}')

