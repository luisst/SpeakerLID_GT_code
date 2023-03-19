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


def speaker_swapping_groups(s_input_ID, current_video_name):

    # Extract facilitator name to choose the matching
    matches_list = re.findall(regex, current_video_name)

    if len(matches_list) > 1:
        sys.error(f'More than session found in name: {current_video_name}')
    if matches_list[0] == 'None':
        sys.error(f'No session found in name: {current_video_name}')

    group_name = matches_list[0]

    # Select matching list according to group name:
    if group_name == 'Irma':
        swap_speaker_list = ['Juan16P','Herminio10P','Irma','Jacinto51P','Jorge17P']

    elif group_name == 'Venkatesh':
        swap_speaker_list = ['Gabino96P','Jesus69P','Leandro99P','VJ']

    elif group_name == 'Allan':
        swap_speaker_list = ['Bryan26P','Mateo59P','Manuel58P','Luis', 'Allan']

    elif group_name == 'Shelby':
        swap_speaker_list = ['Shelby','Cesar61P','Mauricio60P','Karen63P','Emily62P']

    # elif group_name == '':
    #     swap_speaker_list = []

    # elif group_name == '':
    #     swap_speaker_list = []

    # elif group_name == '':
    #     swap_speaker_list = []

    # swap speaker accordingly:
    if s_input_ID not in ['S0', 'S1', 'S2', 'S3', 'S4']:
        sys.error(f'Speaker index is not in format Sx: {s_input_ID}')
    
    index_from_speaker = int(s_input_ID[-1])

    return swap_speaker_list[index_from_speaker]