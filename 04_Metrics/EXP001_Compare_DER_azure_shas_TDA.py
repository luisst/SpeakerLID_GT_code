from pathlib import Path

from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred
from utilities_entropy import log_and_print_entropy, create_histogram


# Root of all results
# root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','EXP-001-001B')
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','EXP-001C')
# original_audios_folder = root_dir.joinpath('GT_Testset_SHAS_Chunks_all _stages','Testset_stage1','input_wavs') 

original_audios_folder = root_dir.joinpath('GT_AzureTestset_SHAS_Chunks_all_stages','Testset_stage1','input_wavs') 

# Load GT list:
GT_pth = root_dir.joinpath('GT_TestSet')

verbose = False
extra_verbose = False
min_overlap_percentage = 0.3

### List of all available models:

## Chunks_SHAS 
ch_shas_pth = root_dir.joinpath('GT_Testset_SHAS_Chunks_all_stages','final_csv')

ch_shas_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_shas_pth, 
        gt_suffix_added='GT', pred_suffix_added='pred',
        gt_ext = 'csv', pred_ext = 'csv')
method_type = 'Chunks_SHAS'

# log_and_print_entropy(root_dir, method_type, ch_shas_matches, ch_shas_pth, min_overlap_percentage, extra_verbose, verbose)
create_histogram(root_dir, method_type, ch_shas_matches, cdf_flag=True)        

## Chunks Keppler mapper
ch_TDA_pth = root_dir.joinpath('GT_Testset_TDA_Chunks_all_stages','final_csv')

ch_TDA_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_TDA_pth, 
        gt_suffix_added='GT', pred_suffix_added='pred',
        gt_ext = 'csv', pred_ext = 'csv')
method_type = 'Chunks_TDA'

# log_and_print_entropy(root_dir, method_type, ch_TDA_matches, ch_TDA_pth, min_overlap_percentage, extra_verbose, verbose)
create_histogram(root_dir, method_type, ch_TDA_matches, cdf_flag=True)        


## Azure file 1 
azure_pth1 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet1')

azure_matches1 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth1, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')
method_type = 'azure'

# log_and_print_entropy(root_dir, method_type, azure_matches1, azure_pth1, min_overlap_percentage, extra_verbose, verbose)
        

## Azure file 2
azure_pth2 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet2')

azure_matches2 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth2, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')
method_type = 'azure'

# log_and_print_entropy(root_dir, method_type, azure_matches2, azure_pth2, min_overlap_percentage, extra_verbose, verbose)

## Azure file 3
azure_pth3 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet3')

azure_matches3 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth3, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')
method_type = 'azure'

# log_and_print_entropy(root_dir, method_type, azure_matches3, azure_pth3, min_overlap_percentage, extra_verbose, verbose)

## Azure all-together
azure_all_pth = root_dir.joinpath('EXP-002_Azure_IrmaTestSet_all')

azure_matches_all = matching_basename_pathlib_gt_pred(GT_pth, azure_all_pth, 
        gt_suffix_added='GT',
        gt_ext = 'csv', pred_ext = 'txt')
method_type = 'azure'

create_histogram(root_dir, method_type, azure_matches_all, cdf_flag=True)        



## Chunks_SHAS 
ch_shas_pth = root_dir.joinpath('GT_AzureTestset_SHAS_Chunks_all_stages','final_csv')

ch_shas_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_shas_pth, 
        gt_suffix_added='GT', pred_suffix_added='pred',
        gt_ext = 'csv', pred_ext = 'csv')
method_type = 'Chunks_SHAS'

log_and_print_entropy(root_dir, method_type, ch_shas_matches, ch_shas_pth, min_overlap_percentage, extra_verbose, verbose)
create_histogram(root_dir, method_type, ch_shas_matches, cdf_flag=True)  


## Chunks Keppler mapper
ch_TDA_pth = root_dir.joinpath('GT_AzureTestset_TDA_Chunks_all_stages','final_csv')

ch_TDA_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_TDA_pth, 
        gt_suffix_added='GT', pred_suffix_added='pred',
        gt_ext = 'csv', pred_ext = 'csv')
method_type = 'Chunks_TDA'

log_and_print_entropy(root_dir, method_type, ch_TDA_matches, ch_TDA_pth, min_overlap_percentage, extra_verbose, verbose)
create_histogram(root_dir, method_type, ch_TDA_matches, cdf_flag=True)        


