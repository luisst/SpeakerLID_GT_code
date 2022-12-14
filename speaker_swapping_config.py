

### From Shelby (S0 and counterclockwise)
def speaker_swapping(s_input_ID):
    # swap speaker accordingly:
    if s_input_ID == 'S0':
        return 'S2'
    elif s_input_ID == 'S1':
        return 'S4'
    elif s_input_ID == 'S2':
        return 'S5'
    elif s_input_ID == 'S3':
        return 'S3'
    elif s_input_ID == 'S4':
        return 'S1'

### From Allan (starts from left to right)
# def speaker_swapping(s_input_ID):
#     # swap speaker accordingly:
#     if s_input_ID == 'S0':
#         return 'S6'
#     elif s_input_ID == 'S1':
#         return 'S5'
#     elif s_input_ID == 'S2':
#         return 'S4'
#     elif s_input_ID == 'S3':
#         return 'S2'
#     elif s_input_ID == 'S4':
#         return 'S1'