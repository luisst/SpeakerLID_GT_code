import sys
import re

from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.metrics.diarization import DiarizationCoverage
from pyannote.metrics.diarization import DiarizationPurity
from pyannote.core import Annotation, Segment

from utilities_functions import find_audio_duration


def gt_format_der(current_transcript_pth):
    # Src	StartTime	EndTime
    # s0s0	3.93	5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]
    lines.pop(0)

    reference = Annotation()
    for line in lines:
        Speaker, Lang, start_time, stop_time = line.split('\t')
        reference[Segment(float(start_time), float(stop_time))] = Speaker 
    
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
    

def der_calculation( current_matches, audios_folder, pred_method='None', suffix_added='', verbose = False ):

    if len(current_matches) == 0:
        print(f'>>>>>>>>>> ERROR: no matches found! in {pred_method}')
        return 0, 0, 0
    
    func_pred = select_method(pred_method)

    all_der = []
    all_der_purity = []
    all_der_cov = []
    for current_gt_pth, current_pred_pth in current_matches:
        current_reference = gt_format_der(current_gt_pth)
        current_hypothesis = func_pred(current_pred_pth)

        current_audio_duration = find_audio_duration(current_gt_pth, audios_folder, suffix_added)

        diarizationErrorRate = DiarizationErrorRate()
        der_dict = diarizationErrorRate(current_reference, current_hypothesis, detailed=True, uem=Segment(0, current_audio_duration))
        current_der = der_dict['diarization error rate']
        all_der.append(current_der)

        purity = DiarizationPurity()
        purity_dict = purity(current_reference, current_hypothesis, detailed=True, uem=Segment(0, current_audio_duration))
        current_purity = purity_dict['purity']
        all_der_purity.append(current_purity)

        coverage = DiarizationCoverage()
        cov_dict = coverage(current_reference, current_hypothesis, detailed=True, uem=Segment(0, current_audio_duration))
        current_cov = cov_dict['coverage']
        all_der_cov.append(current_cov)

        false_speech_ratio = round((der_dict['false alarm'] / current_audio_duration)*100, 1)
        missed_det_ratio = round((der_dict['missed detection'] / current_audio_duration)*100, 1)
        confusion_ratio = round((der_dict['confusion'] / der_dict['total'])*100, 1)

        print(f'\n\n\t{current_gt_pth.stem}')
        print(f'DER: {(current_der*100):.2f}\tF_speech: {false_speech_ratio}\tF_bck: {missed_det_ratio}\tConf: {confusion_ratio}\t|\tPurity: {(current_purity*100):.2f}\tCoverage: {(current_cov*100):.2f}')
        print(f'\nBest matching: {diarizationErrorRate.optimal_mapping(current_reference, current_hypothesis)}')

        if verbose:
            print(f'\nDetails:')
            for key, value in der_dict.items():
                print(f"\t{key}: {value:.2f}")

            for key, value in purity_dict.items():
                print(f"pur: {key}: {value:.2f}")

            for key, value in cov_dict.items():
                print(f"cov: {key}: {value:.2f}")
    
    avg_der = sum(all_der) / len(all_der)
    avg_purity = sum(all_der_purity) / len(all_der_purity)
    avg_cov = sum(all_der_cov) / len(all_der_cov)
    return avg_der, avg_purity, avg_cov


def extract_basename(input_str, suffix_added):
    mymatch = re.search(r'.+(?=_{})'.format(suffix_added), input_str)
    if mymatch != None:
        mystring = mymatch.group()    
    else:
        mystring = ''
    return mystring


def matching_basename_pathlib_gt_pred(GT_pth, pred_pth, 
        gt_suffix_added='', pred_suffix_added='',
        gt_ext = 'txt', pred_ext = 'txt', verbose = False):

    if gt_suffix_added == '':
        GT_list = sorted(list(GT_pth.glob(f'*.{gt_ext}')))
    else:
        GT_list = sorted(list(GT_pth.glob(f'*_{gt_suffix_added}.{gt_ext}')))

    if pred_suffix_added == '':
        pred_list = sorted(list(pred_pth.glob(f'*.{pred_ext}')))
    else:
        pred_list = sorted(list(pred_pth.glob(f'*_{pred_suffix_added}.{pred_ext}')))


    if len(GT_list) == 0:
        print(f'ERROR GT list empty. Check suffix')
    
    if len(pred_list) == 0:
        print(f'ERROR!! Pred list is empty. Check suffix')

    # Extract basenames from pathlib

    if gt_suffix_added == '':
        gt_list_basenames = [x.stem for x in GT_list]
    else:
        gt_list_basenames = [extract_basename(x.name, gt_suffix_added) for x in GT_list]

    if pred_suffix_added == '':
        pred_list_basenames = [x.stem for x in pred_list]
    else:
        pred_list_basenames = [extract_basename(x.name, pred_suffix_added) for x in pred_list]

    if verbose:
        print(f'GT: {gt_list_basenames}\nPred: {pred_list_basenames}')

    # Check for duplicates
    if len(gt_list_basenames) != len(list(set(gt_list_basenames))):
        sys.exit(f'Duplicates found at folder {GT_pth}')

    if len(pred_list_basenames) != len(list(set(pred_list_basenames))):
        sys.exit(f'Duplicates found at folder {pred_pth}')

    gt_idxs = []
    for idx, current_gt in enumerate(gt_list_basenames):
        if current_gt in pred_list_basenames:
            gt_idxs.append(idx)

    pred_idxs = []
    for idx, current_pred in enumerate(pred_list_basenames):
        if current_pred in gt_list_basenames:
            pred_idxs.append(idx)

    # Verify same length
    if len(gt_idxs) != len(pred_idxs):
        sys.exit(f'matching indexes are not equal!')

    # Return the tuples
    matching_list = []
    for idx in range(0, len(gt_idxs)):
        matching_list.append((GT_list[gt_idxs[idx]], pred_list[pred_idxs[idx]]))

    # if verbose:
        # print(matching_list)

    return matching_list