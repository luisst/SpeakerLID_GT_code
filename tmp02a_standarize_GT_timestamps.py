
from pathlib import Path

tmp_nm = 'tmp_order_test.csv'
csv_input_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022',
'GT_speakerLID', 'G-C2L1P-Feb16-B-Shelby_q2_03-05', 'to_praat', tmp_nm)

# Load 1 csv file
f = open(str(csv_input_pth), 'r')
lines = f.readlines()
f.close()

# For loop -> 5 different speakers (dict)
gt_dict = {'S0':[],
        'S1':[],
        'S2':[],
        'S3':[],
        'S4':[]}

lines.pop(0)
for line in lines:
    speaker_IDLang, strt_time, end_time = line.split('\t')
    speaker_ID = speaker_IDLang[:2]
    speaker_lang = speaker_IDLang[2:]
    end_time = end_time.strip()

    gt_dict[speaker_ID].append([speaker_lang, strt_time, end_time])

# order the timestamps
current_key = 'S0'
current_list_times = gt_dict[current_key]

sorted_times = sorted(current_list_times, key=lambda x: float(x[1]))
# TO-DO: detect overlap, back-to-back and small distances