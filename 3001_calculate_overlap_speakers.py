import math
import sys
from pathlib import Path

# Read aws transcript
aws_txt_pth = Path.home().joinpath('Dropbox', '04_Audio_Perfomance_Evaluation','AWS_speech_recognition','results_aws_Dec22')
aws_suffix_added = 'awspred'
aws_pred_list = sorted(list(aws_txt_pth.glob(f'*_{aws_suffix_added}.txt')))

# Read GT
GT_txt_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID','G-C2L1P-Feb16-B-Shelby_q2_03-05','ftDiarization01')
gt_suffix_added = 'praat_done_ready'
GT_list = sorted(list(GT_txt_pth.glob(f'*_{gt_suffix_added}.csv')))

if len(aws_pred_list) != len(GT_list):
    sys.exit('Number of files are different')

## For loop each file txt
errors_total_list = []

for idx in range(0, len(GT_list)):
    current_gt_pth = GT_list[idx]
    current_awspred_pth = aws_pred_list[idx]
    # Find the largest amount of speaking per speaker:

    f = open(current_gt_pth, 'r')
    lines = f.readlines()
    f.close()

    lines.pop(0)
    speakers_length = {}
    for line in lines :
        SpeakerLang, start_time, end_time = line.split('\t')
        end_time = end_time.strip()
        current_duration = float(end_time) - float(start_time)

        speaker_ID = SpeakerLang[0:2]

        if speaker_ID not in speakers_length:
            speakers_length[speaker_ID] = current_duration
        else:
            speakers_length[speaker_ID] =+ current_duration

    print(f'{current_gt_pth.stem}\n{speakers_length}')


    f = open(current_awspred_pth, 'r')
    lines = f.readlines()
    f.close()

    pred_length_aws = {}
    for line in lines :
        SpeakerLang, start_time, end_time = line.split('\t')
        end_time = end_time.strip()
        current_duration = float(end_time) - float(start_time)

        speaker_ID = SpeakerLang[0:2]

        if speaker_ID not in pred_length_aws:
            pred_length_aws[speaker_ID] = current_duration
        else:
            pred_length_aws[speaker_ID] =+ current_duration

    print(f'{current_awspred_pth.stem}\n{pred_length_aws}')

    # Sort them
    speakers_ordered_keys = sorted(speakers_length, key=speakers_length.get, reverse=True)
    aws_ordered_keys = sorted(pred_length_aws, key=pred_length_aws.get, reverse=True)

    # Match the speaker in the line, discard the little one? 
    # is better to match them with their closest match <-- future

    matches_length = min(len(speakers_ordered_keys), len(aws_ordered_keys))

    combined_dict = {}
    total_length_per_speaker = []
    for i in range(0, matches_length):
        combined_dict[i] = [speakers_length[speakers_ordered_keys[i]], pred_length_aws[aws_ordered_keys[i]]]

    print(f'lengths per speaker: {combined_dict}')

    ################## Total time of Speech vs Non Speech ########################
    gt_totals = sum(speakers_length.values())
    aws_totals = sum(pred_length_aws.values())

    diff_totals = math.sqrt((gt_totals - aws_totals)**2)
    error_total = (diff_totals*100)/gt_totals
    print(f'This is the error from the totals: {error_total:.2f} \t difference MSE: {diff_totals:.2f} \t gt_totals: {gt_totals:.2f} \t aws_totals: {aws_totals:.2f}')

    errors_total_list.append(error_total)

    ################## MSE of measures per speaker ###############################
    # generate array of speaker lengths 


    ################### Fine calculating the speakers overlaps with the timestamps
    # For each speaker
    # Great for loop across the GT portions
    # for key in combined_dict:
