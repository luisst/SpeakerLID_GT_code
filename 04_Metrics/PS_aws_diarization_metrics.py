import re
import sys
from pathlib import Path

from utilities_functions import matching_basename_pathlib_gt_pred
from pyannote.core import Annotation, Segment


def check_header(filename):
    f = open(filename, 'r')
    first = f.read(1)
    f.close()
    return first not in '.-0123456789'


# Read aws transcript
pred_pth = Path.home().joinpath('Dropbox', '04_Audio_Perfomance_Evaluation','AWS_speech_recognition','results_aws_Dec22')

# Read GT
GT_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID','G-C2L1P-Feb16-B-Shelby_q2_03-05','final_csv')

matched_tuples = matching_basename_pathlib_gt_pred(GT_pth, pred_pth, 
        gt_suffix_added='praat_done_ready', pred_suffix_added='awspred',
        gt_ext = 'csv', pred_ext = 'txt')

all_der_values = []

for current_gt_pth, current_pred_pth in matched_tuples:
    print(current_gt_pth) 

    current_gt_pth = matched_tuples[0][0]
    current_pred_pth = matched_tuples[0][1]

    check_header(current_gt_pth)
    with open(current_gt_pth) as f:
        lines = [line.rstrip() for line in f]

    lines.pop(0)

    reference = Annotation()
    for line in lines:
        SpeakerLang, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = SpeakerLang


    with open(current_pred_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        SpeakerLang, start_time, stop_time = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = SpeakerLang

    from pyannote.metrics.diarization import DiarizationErrorRate
    diarizationErrorRate = DiarizationErrorRate()
    print("DER = {0:.3f}".format(diarizationErrorRate(reference, hypothesis, uem=Segment(0, 40))))

    print(f'\nBest matching:')
    print(diarizationErrorRate.optimal_mapping(reference, hypothesis))

    print(f'\nDetails:')
    print(diarizationErrorRate(reference, hypothesis, detailed=True, uem=Segment(0, 40)))

    from pyannote.metrics.diarization import DiarizationPurity
    purity = DiarizationPurity()
    print("Purity = {0:.3f}".format(purity(reference, hypothesis, uem=Segment(0, 40))))

    from pyannote.metrics.diarization import DiarizationCoverage
    coverage = DiarizationCoverage()
    print("Coverage = {0:.3f}".format(coverage(reference, hypothesis, uem=Segment(0, 40))))