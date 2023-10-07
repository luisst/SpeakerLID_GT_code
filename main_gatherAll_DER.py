
import sys
from pathlib import Path

from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.metrics.diarization import DiarizationCoverage
from pyannote.metrics.diarization import DiarizationPurity
from pyannote.core import Annotation, Segment

from utilities_functions import matching_basename_pathlib_gt_pred, extract_basename, get_total_video_length, find_audio_duration


def gt_format_der(current_transcript_pth):
    # Src	StartTime	EndTime
    # s0s0	3.93	5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]
    lines.pop(0)

    reference = Annotation()
    for line in lines:
        SpeakerLang, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = SpeakerLang 
    
    return reference


def aws_format_der(current_transcript_pth):
    # Talking60_easy_rnd-006.wav	spk_0	en-US	1.31	2.14	Okay	0.4618

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        fname, my_source, my_lang, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = my_source 
    
    return hypothesis


def azure_format_der(current_transcript_pth):
    # 1	0.33	1.12	Try to run it again.	0.7578845

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        my_source, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = my_source 
    
    return hypothesis


def select_method(pred_method):
    if pred_method == 'aws':
        return aws_format_der
    elif pred_method == 'azure':
        return azure_format_der
    

def der_calculation(pred_method, current_matches, audios_folder, suffix_added, verbose = False ):

    if len(current_matches) == 0:
        print(f'ERROR: no matches found! in {pred_method}')
        return 0
    
    func_pred = select_method(pred_method)

    all_der = []
    all_der_purity = []
    all_der_cov = []
    for current_gt_pth, current_pred_pth in current_matches:
        current_reference = gt_format_der(current_gt_pth)
        current_hypothesis = func_pred(current_pred_pth)

        current_audio_duration = find_audio_duration(current_gt_pth, audios_folder, suffix_added)

        diarizationErrorRate = DiarizationErrorRate()
        all_der.append(diarizationErrorRate(current_reference, current_hypothesis, uem=Segment(0, current_audio_duration)))

        purity = DiarizationPurity()
        all_der_purity.append(purity(current_reference, current_hypothesis, uem=Segment(0, current_audio_duration)))

        coverage = DiarizationCoverage()
        all_der_cov.append(coverage(current_reference, current_hypothesis, uem=Segment(0, current_audio_duration)))


        if verbose:
            print(f'\nDER: {(all_der[-1]*100):.2f}')
            print(f'Best matching:')
            print(diarizationErrorRate.optimal_mapping(current_reference, current_hypothesis))

            print(f'\nDetails:')
            print(diarizationErrorRate(current_reference, current_hypothesis, detailed=True, uem=Segment(0, current_audio_duration)))

            print(f'Purity = {(all_der_purity[-1]*100):.3f}')
            print(f'Coverage = {(all_der_cov[-1]*100):.3f}')
    
    return [sum(all_der) / len(all_der), sum(all_der_purity) / len(all_der_purity), sum(all_der_cov) / len(all_der_cov)]


# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Conversation_SpeakerDiarization','SDpart1','All_results')
audios_folder = root_dir.parent 

# Load GT list:
GT_pth = root_dir.parent.joinpath('GT','final_csv')


### List of all available models:

# # AWS 
# aws_pth = root_dir.joinpath('aws','final_csv')

# aws_matches = matching_basename_pathlib_gt_pred(GT_pth, aws_pth, 
#         gt_suffix_added='praat_done_ready', pred_suffix_added='awspred',
#         gt_ext = 'csv', pred_ext = 'txt')

# aws_der, aws_purity, aws_cov  =  der_calculation('aws', aws_matches, audios_folder, 'praat_done_ready' )
# der_inverted = 1 - aws_der
# print(f'aws -> \tDER: {aws_der:.2f} | {der_inverted:.2f} \tPurity: {(aws_purity*100):.2f} \tCoverage: {(aws_cov*100):.2f}')

# azure 
azure_pth = root_dir.joinpath('azure','final_csv')

azure_matches = matching_basename_pathlib_gt_pred(GT_pth, azure_pth, 
        gt_suffix_added='praat_done_ready', pred_suffix_added='raw',
        gt_ext = 'csv', pred_ext = 'txt')

azure_der, azure_purity, azure_cov =  der_calculation('azure', azure_matches, audios_folder, 'praat_done_ready')
der_inverted = 1 - azure_der
print(f'azure -> \tDER: {azure_der:.2f} | {der_inverted:.2f} \tPurity: {(azure_purity*100):.2f} \tCoverage: {(azure_cov*100):.2f}')