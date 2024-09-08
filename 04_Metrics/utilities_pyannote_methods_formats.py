from pyannote.core import Annotation, Segment

## VAD methods

def select_method(pred_method):
    if pred_method == 'audiotok' or \
        pred_method == 'shas' or \
        pred_method == 'BAS' or \
        pred_method == 'cobra' or \
        pred_method == 'silero':
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

def vad_format(current_transcript_pth):
    # Src	StartTime	EndTime
    # s0s0	3.93	5.86
    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]
    lines.pop(0)

    reference = Annotation()
    for line in lines:
        Speaker, Lang, start_time, stop_time = line.split('\t')
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

# # Cobra 
# cobra_pth = root_dir.joinpath('cobra','joined_timestamps')

# cobra_matches = matching_basename_pathlib_gt_pred(GT_pth, cobra_pth, 
#         gt_suffix_added='done_ready', pred_suffix_added='pico0.3',
#         gt_ext = 'csv', pred_ext = 'csv')

# cobra_acc =  vad_calculation('cobra', cobra_matches, detection_method = detection_method, verbose = verbose)
# print(f'cobra: {(cobra_acc):.2f}')

# # Audiotok: 
# audiotok_pth = root_dir.joinpath('auditok','joined_timestamps')

# audiotok_matches = matching_basename_pathlib_gt_pred(GT_pth, audiotok_pth, 
#         gt_suffix_added='done_ready', pred_suffix_added='ener75',
#         gt_ext = 'csv', pred_ext = 'csv')

# audiotok_acc =  vad_calculation('audiotok', audiotok_matches, detection_method = detection_method, verbose = verbose)
# print(f'audiotok: {(audiotok_acc):.2f}')

# # BAS vad website:
# BAS_pth = root_dir.joinpath('BAS','simplified')

# BAS_matches = matching_basename_pathlib_gt_pred(GT_pth, BAS_pth, 
#         gt_suffix_added='done_ready', 
#         gt_ext = 'csv', pred_ext = 'csv')

# BAS_acc =  vad_calculation('BAS', BAS_matches, detection_method = detection_method, verbose = verbose)
# print(f'BAS website: {(BAS_acc):.2f}')

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

# # inaSpeechSegmenter
# inaSS_pth = root_dir.joinpath('inaSpeechSegmenter')

# inaSS_matches = matching_basename_pathlib_gt_pred(GT_pth, inaSS_pth, 
#         gt_suffix_added='done_ready',
#         gt_ext = 'csv', pred_ext = 'csv')

# inaSS_acc =  vad_calculation('inaSS', inaSS_matches, detection_method = detection_method, verbose = verbose)
# print(f'inaSpeechSegmenter: {(inaSS_acc):.2f}')

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

# # SpeechBrain crdnn
# speechbrain_pth = root_dir.joinpath('vad-crdnn-libriparty', 'final_csv')

# speechbrain_matches = matching_basename_pathlib_gt_pred(GT_pth, speechbrain_pth, 
#         gt_suffix_added='done_ready',
#         gt_ext = 'csv', pred_ext = 'csv')

# speechbrain_acc =  vad_calculation('speechbrain', speechbrain_matches, detection_method = detection_method, verbose = verbose)
# print(f'speechbrain: {(speechbrain_acc):.2f}')


def whisper_format(current_transcript_pth):
    # Speech	en	38.0	39.0	I can't.	0.012211376801133001

    with open(current_transcript_pth) as f:
        try:
            with open(current_transcript_pth, encoding="utf8") as f:
                lines = [line.rstrip() for line in f]
        except UnicodeDecodeError as e:
            if str(e) == "'charmap' codec can't decode byte 0x90 in position 1100: character maps to <undefined>'":
                import pdb; pdb.set_trace()
            else:
                raise e

    hypothesis = Annotation()
    for line in lines:
        my_source, my_lang, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        
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

# # AWS 
# aws_pth = root_dir.joinpath('aws','final_csv')

# aws_matches = matching_basename_pathlib_gt_pred(GT_pth, aws_pth, 
#         gt_suffix_added='done_ready', pred_suffix_added='awspred',
#         gt_ext = 'csv', pred_ext = 'txt')

# aws_acc =  vad_calculation('aws', aws_matches, detection_method = detection_method, verbose = verbose)
# print(f'aws: {(aws_acc):.2f}')

def azure_format(current_transcript_pth):
    # 1	0.33	1.12	Try to run it again.	0.7578845

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    hypothesis = Annotation()
    for line in lines:
        my_source, start_time, stop_time, txt_pred, my_prob = line.split('\t')
        hypothesis[Segment(float(start_time), float(stop_time))] = 'speech'
    
    return hypothesis