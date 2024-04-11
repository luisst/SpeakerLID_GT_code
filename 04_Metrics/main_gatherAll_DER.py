
from pathlib import Path

from utilities_pyannote_metrics import der_calculation, matching_basename_pathlib_gt_pred


# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD','All_results')
audios_folder = root_dir.parent.joinpath('WAV_FILES') 

# Load GT list:
GT_pth = root_dir.parent.joinpath('GT_csv')


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
azure_pth = root_dir.joinpath('azure','final_csv_v31')

azure_matches = matching_basename_pathlib_gt_pred(GT_pth, azure_pth, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')

azure_der, azure_purity, azure_cov =  der_calculation(azure_matches, audios_folder, pred_method='azure', suffix_added='GT', verbose=False)
der_inverted = 1 - azure_der
print(f'azure -> \tDER: {azure_der:.2f} | {der_inverted:.2f} \tPurity: {(azure_purity*100):.2f} \tCoverage: {(azure_cov*100):.2f}')

