
import sys
from pathlib import Path

from pyannote.metrics.diarization import DiarizationCoverage
from pyannote.metrics.diarization import DiarizationPurity
from pyannote.metrics.detection import DetectionAccuracy, DetectionErrorRate
from pyannote.core import Annotation, Segment

from utilities_functions import matching_basename_pathlib_gt_pred


def vad_format(current_transcript_pth):
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

def audiotok_format(current_transcript_pth):
    # 'voice	0.10	20.1'
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        _ , start_time, stop_time = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def inaSS_format(current_transcript_pth):
    # 'male/female/music/noise	0.10	20.1'

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        my_source , start_time, stop_time = line.split('\t')
        if my_source == 'male' or my_source == 'female': 
            hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def speechbrain_format(current_transcript_pth):
    # 'male/female/music/noise	0.10	20.1'

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        _ , start_time, stop_time, my_source = line.split('\t')
        if my_source == 'SPEECH' : 
            hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def whisper_format(current_transcript_pth):
    # Speech	en	38.0	39.0	I can't.	0.012211376801133001

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        my_source, my_lang, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        if my_source == 'Speech' : 
            hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def aws_format(current_transcript_pth):
    # Talking60_easy_rnd-006.wav	spk_0	en-US	1.31	2.14	Okay	0.4618

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        fname, my_source, my_lang, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def azure_format(current_transcript_pth):
    # 1	0.33	1.12	Try to run it again.	0.7578845

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        my_source, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis


def select_method(pred_method):
    if pred_method == 'audiotok' or pred_method == 'shas' or pred_method == 'BAS' or pred_method == 'cobra':
        return audiotok_format
    elif pred_method == 'inaSS':
        return inaSS_format
    elif pred_method == 'speechbrain':
        return speechbrain_format
    elif pred_method == 'whisper':
        return whisper_format
    elif pred_method == 'aws':
        return aws_format
    elif pred_method == 'azure':
        return azure_format
    

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
        # print(f'DER: {current_DER}')

        all_vad_acc.append(current_DER)
    
    return sum(all_vad_acc) / len(all_vad_acc)


# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','All_results')

# Load GT list:
GT_pth = root_dir.parent.joinpath('GT','final_csv')


### List of all available models:

# Audiotok: 
audiotok_pth = root_dir.joinpath('auditok','joined_timestamps')

audiotok_matches = matching_basename_pathlib_gt_pred(GT_pth, audiotok_pth, 
        gt_suffix_added='done_ready', pred_suffix_added='ener75',
        gt_ext = 'csv', pred_ext = 'csv')

audiotok_acc =  vad_calculation('audiotok', audiotok_matches)
# print(f'audiotok: {(audiotok_acc*100):.2f}')
print(f'audiotok: {(audiotok_acc):.2f}')

# BAS vad website:
BAS_pth = root_dir.joinpath('BAS','simplified')

BAS_matches = matching_basename_pathlib_gt_pred(GT_pth, BAS_pth, 
        gt_suffix_added='done_ready', 
        gt_ext = 'csv', pred_ext = 'csv')

BAS_acc =  vad_calculation('BAS', BAS_matches)
# print(f'BAS website: {(BAS_acc*100):.2f}')
print(f'BAS website: {(BAS_acc):.2f}')

# Cobra 
cobra_pth = root_dir.joinpath('cobra','joined_timestamps')

cobra_matches = matching_basename_pathlib_gt_pred(GT_pth, cobra_pth, 
        gt_suffix_added='done_ready', pred_suffix_added='pico0.3',
        gt_ext = 'csv', pred_ext = 'csv')

cobra_acc =  vad_calculation('cobra', cobra_matches)
# print(f'cobra: {(cobra_acc*100):.2f}')
print(f'cobra: {(cobra_acc):.2f}')

# inaSpeechSegmenter
inaSS_pth = root_dir.joinpath('inaSpeechSegmenter')

inaSS_matches = matching_basename_pathlib_gt_pred(GT_pth, inaSS_pth, 
        gt_suffix_added='done_ready',
        gt_ext = 'csv', pred_ext = 'csv')

inaSS_acc =  vad_calculation('inaSS', inaSS_matches)
# print(f'inaSpeechSegmenter: {(inaSS_acc*100):.2f}')
print(f'inaSpeechSegmenter: {(inaSS_acc):.2f}')

# SHAS
shas_pth = root_dir.joinpath('shas')

shas_matches = matching_basename_pathlib_gt_pred(GT_pth, shas_pth, 
        gt_suffix_added='done_ready',
        gt_ext = 'csv', pred_ext = 'txt')

shas_acc =  vad_calculation('shas', shas_matches)
# print(f'shas: {(shas_acc*100):.2f}')
print(f'shas: {(shas_acc):.2f}')

# SpeechBrain crdnn
speechbrain_pth = root_dir.joinpath('vad-crdnn-libriparty', 'final_csv')

speechbrain_matches = matching_basename_pathlib_gt_pred(GT_pth, speechbrain_pth, 
        gt_suffix_added='done_ready',
        gt_ext = 'csv', pred_ext = 'csv')

speechbrain_acc =  vad_calculation('speechbrain', speechbrain_matches)
# print(f'speechbrain: {(speechbrain_acc*100):.2f}')
print(f'speechbrain: {(speechbrain_acc):.2f}')

# Whisper openAI
whisper_pth = root_dir.joinpath('whisper','final_csv')

whisper_matches = matching_basename_pathlib_gt_pred(GT_pth, whisper_pth, 
        gt_suffix_added='done_ready',
        gt_ext = 'csv', pred_ext = 'txt')

whisper_acc =  vad_calculation('whisper', whisper_matches)
# print(f'whisper: {(whisper_acc*100):.2f}')
print(f'whisper: {(whisper_acc):.2f}')

# AWS 
aws_pth = root_dir.joinpath('aws','final_csv')

aws_matches = matching_basename_pathlib_gt_pred(GT_pth, aws_pth, 
        gt_suffix_added='done_ready', pred_suffix_added='awspred',
        gt_ext = 'csv', pred_ext = 'txt')

aws_acc =  vad_calculation('aws', aws_matches)
# print(f'aws: {(aws_acc*100):.2f}')
print(f'aws: {(aws_acc):.2f}')

# azure 
azure_pth = root_dir.joinpath('azure','final_csv')

azure_matches = matching_basename_pathlib_gt_pred(GT_pth, azure_pth, 
        gt_suffix_added='done_ready', pred_suffix_added='raw',
        gt_ext = 'csv', pred_ext = 'txt')

azure_acc =  vad_calculation('azure', azure_matches)
# print(f'azure: {(azure_acc*100):.2f}')
print(f'azure: {(azure_acc):.2f}')