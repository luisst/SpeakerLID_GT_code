import sys
import re


regex = r"(?<=[a-zA-Z]{3}\d{2}-[a-zA-Z]-)\w*?(?=_)"

def speaker_swapping_tony(s_input_ID, current_video_name):

    # Extract facilitator name to choose the matching
    matches_list = re.findall(regex, current_video_name)

    if len(matches_list) > 1:
        sys.error(f'More than session found in name: {current_video_name}')
    if matches_list[0] == 'None':
        sys.error(f'No session found in name: {current_video_name}')

    group_name = matches_list[0]

    # Select matching list according to group name:
    if group_name == 'Shelby':
        # From Shelby (S0 and counterclockwise)
        swap_speaker_list = ['S2', 'S4', 'S5', 'S3', 'S1']
    elif group_name == 'Allan':
        swap_speaker_list = ['S6', 'S5', 'S4', 'S2', 'S1']

    # swap speaker accordingly:
    if s_input_ID not in ['S0', 'S1', 'S2', 'S3', 'S4']:
        sys.error(f'Speaker index is not in format Sx: {s_input_ID}')
    
    index_from_speaker = int(s_input_ID[-1])

    return swap_speaker_list[index_from_speaker]


def speaker_swapping_groups(s_input_ID, current_video_name,
                            lang_csv, session_name_full = False):
                        
    if session_name_full:
        session_name = current_video_name
    else:
        session_name = '-'.join(current_video_name.split('-')[:-1])

    # Select matching list according to group name:

    ## Training set
    if session_name == 'G-C1L1P-Mar02-E-Irma_q2_03-08':
        swap_speaker_list = ['Juan16P','Herminio10P','Irma','Jacinto51P','Jorge17P']

    elif session_name == 'Venkatesh':
        swap_speaker_list = ['Gabino96P','Jesus69P','Leandro99P','VJ']

    elif session_name== 'G-C2L1P-Apr12-A-Allan_q2_04-05':
        swap_speaker_list = ['Bryan26P','Mateo59P','Manuel58P','Luis']

    elif session_name== 'Shelby':
        swap_speaker_list = ['Shelby','Cesar61P','Mauricio60P','Karen63P','Emily62P']

    elif session_name== 'Jenny':
        swap_speaker_list = ['Jessy102P','Eric101P','Emily62P','Hannah100P','Jenny']


    ## Test set
    elif session_name== 'G-C2L1P-Apr26-A-Allan_q2_02-05' \
        or session_name== 'G-C2L1P-Apr26-A-Allan_q2_03-05' \
        or session_name== 'G-C2L1P-Apr26-A-Allan_q2_04-05':
        swap_speaker_list = ['Bryan26P','Mateo59P','Manuel58P','Allan','Marios']
    
    ## Test set
    elif session_name == 'G-C1L1P-Apr27-E-Irma_q2_03-08' \
        or session_name == 'G-C1L1P-Apr27-E-Irma_q2_04-08' \
        or session_name == 'G-C1L1P-Apr27-E-Irma_q2_05-08':
        swap_speaker_list = ['Juan16P','Herminio10P','Irma','Jacinto51P','Jorge17P']

    ## Test set
    elif session_name== 'G-C2L1P-Apr26-B-Liz_q2_02-06':
        swap_speaker_list = ['Liz', 'Cindy', 'Mauricio60P', 'Emily62P', 'Karen63P']

    ## Test set
    elif session_name== 'G-C2L1P-Apr26-B-Liz_q2_03-06':
        swap_speaker_list = ['Liz', 'Cindy', 'Marios', 'Karen63P', 'Emily62P' ]

    ## Test set -- Extra S2: Mauricio60P
    elif session_name== 'G-C2L1P-Apr26-B-Liz_q2_04-06':
        swap_speaker_list = ['Liz', 'Cindy', 'Cesar61P', 'Karen63P', 'Emily62P' ]
    
    ## Test set -- Extra S4: Phuong
    elif session_name== 'G-C2L1P-Apr26-E-Krithika_q2_03-06' \
        or session_name== 'G-C2L1P-Apr26-E-Krithika_q2_04-06': 
        swap_speaker_list = ['Beto71P','Guillermo72P','Katiana73P','Herminio10P','Krithika']
    
    else:
        sys.exit(f'Session name not found: {session_name}')

    # elif group_name == '':
    #     swap_speaker_list = []

    # elif group_name == '':
    #     swap_speaker_list = []

    # swap speaker accordingly:
    if s_input_ID not in ['S0', 'S1', 'S2', 'S3', 'S4']:
        sys.exit(f'Speaker index is not in format Sx: {s_input_ID}')
    
    index_from_speaker = int(s_input_ID[-1])

    speaker_ID = swap_speaker_list[index_from_speaker]

    if lang_csv not in ['Spa', 'Eng', 'SPA', 'ENG', 'spa', 'eng']:
        print(f'\n\n>>>>>>>>>>>>>>> found new speaker! {lang_csv}')
        speaker_ID = lang_csv

    return speaker_ID 