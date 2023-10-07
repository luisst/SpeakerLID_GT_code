import re
import sys
from pathlib import Path

from utilities_functions import matching_basename_pathlib_gt_pred
import simpleder

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

# for current_gt_pth, current_pred_pth in matched_tuples:
#     print(current_gt_pth) 

current_gt_pth = matched_tuples[0][0]
current_pred_pth = matched_tuples[0][1]

# ref = [("A", 0.0, 1.0),
#        ("B", 1.0, 1.5),
#        ("A", 1.6, 2.1)]

check_header(current_gt_pth)
current_ref = []
with open(current_gt_pth) as f:
    lines = [line.rstrip() for line in f]

lines.pop(0)
for line in lines:
    SpeakerLang, start_time, stop_time = line.split('\t')
    current_ref.append((SpeakerLang, float(start_time), float(stop_time)))

current_hyp = []
with open(current_pred_pth) as f:
    lines = [line.rstrip() for line in f]

for line in lines:
    SpeakerLang, start_time, stop_time = line.split('\t')
    current_hyp.append((SpeakerLang, float(start_time), float(stop_time)))

# hyp = [("1", 0.0, 0.8),
#        ("2", 0.8, 1.4),
#        ("3", 1.5, 1.8),
#        ("1", 1.8, 2.0)]

error = simpleder.DER(current_ref, current_hyp)

print("DER={:.3f}".format(error))