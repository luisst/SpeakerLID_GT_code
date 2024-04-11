from pathlib import Path

from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred
from utilities_entropy import log_and_print_entropy, create_histogram


def single_pred(root_dir, method_csv_pth, method_type, method_run_name, methods_dict, verbose=False, extra_verbose=False, min_overlap_percentage=0.3):
    original_audios_folder = root_dir.joinpath(method_folder,'Testset_stage1','input_wav') 
    # Load GT list:
    GT_pth = root_dir.joinpath('GT_TestSet')

    verbose = False
    extra_verbose = False
    min_overlap_percentage = 0.3

    method_matches = matching_basename_pathlib_gt_pred(GT_pth, method_csv_pth, 
            gt_suffix_added='GT', pred_suffix_added=methods_dict[method_type]['pred_suffix_added'],
            gt_ext = 'csv', pred_ext = methods_dict[method_type]['pred_ext'])

    log_and_print_entropy(root_dir, method_type, method_run_name, method_matches, method_csv_pth, min_overlap_percentage, extra_verbose, verbose)
    create_histogram(root_dir, method_type, method_run_name, method_matches, cdf_flag=True)        


def azure_multiple_wavs(root_dir, method_folder, method_type, methods_dict, verbose=False, extra_verbose=False, min_overlap_percentage=0.3):

    method_pred_pth = root_dir.joinpath(method_folder)

    # Read all txt files in the method_folder
    all_azure_files = list(method_pred_pth.glob('*.txt'))

    # Check if there are files in the folder
    if len(all_azure_files) == 0:
        print(f'WARNING!!! \t No files found in {method_pred_pth}')

    # Create a folder for each file in all_azure_files
    for azure_file in all_azure_files:
        azure_folder = method_pred_pth.joinpath(azure_file.stem)
        azure_folder.mkdir(exist_ok=True, parents=True)

        # Move the file to the folder
        azure_file.rename(azure_folder.joinpath(azure_file.name))


    # Iterate over all folders in the method_folder
    for azure_part_folder in method_pred_pth.iterdir():
        if azure_part_folder.is_dir():
            current_azure_run = azure_part_folder.stem

            single_pred(root_dir, 
                        azure_part_folder,
                        method_type,
                        current_azure_run,
                        methods_dict,
                        verbose=verbose,
                        extra_verbose=extra_verbose,
                        min_overlap_percentage=min_overlap_percentage)


def run_single_pred(root_dir, method_folder, method_type, methods_dict, verbose=False, extra_verbose=False, min_overlap_percentage=0.3):

    if method_type == 'azure':
        azure_multiple_wavs(root_dir,
                            method_folder,
                            method_type,
                            methods_dict,
                            verbose=verbose,
                            extra_verbose=extra_verbose,
                            min_overlap_percentage=min_overlap_percentage)
    else:
        method_csv_pth = root_dir.joinpath(method_folder,'Testset_stage4','final_csv')

        single_pred(root_dir, 
                    method_csv_pth,
                    method_type,
                    method_folder,
                    methods_dict,
                    verbose=verbose,
                    extra_verbose=extra_verbose,
                    min_overlap_percentage=min_overlap_percentage)

# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','EXP-001-Liz')

## Methods available: 'Chunks_SHAS', 'Chunks_TDA', 'azure'
method_type = 'azure'

method_folder='Azure_Liz_All'

methods_dict = {'Chunks_SHAS': {'pred_suffix_added':'pred', 'pred_ext':'csv'},
                'Chunks_TDA': {'pred_suffix_added':'pred', 'pred_ext':'csv'},
                'azure': {'pred_suffix_added':'', 'pred_ext':'txt'}}

verbose = False
extra_verbose = False
min_overlap_percentage = 0.3
#### ---------------------- ####

run_single_pred(root_dir, 
            method_folder,
            method_type,
            methods_dict,
            verbose=verbose,
            extra_verbose=extra_verbose,
            min_overlap_percentage=min_overlap_percentage)



# ## Azure file 1 
# azure_pth1 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet1')

# azure_matches1 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth1, 
#         gt_suffix_added='GT',
#         gt_ext = 'csv', pred_ext = 'txt')
# method_type = 'azure'

# # log_and_print_entropy(root_dir, method_type, azure_matches1, azure_pth1, min_overlap_percentage, extra_verbose, verbose)
        

# ## Azure file 2
# azure_pth2 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet2')

# azure_matches2 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth2, 
#         gt_suffix_added='GT',
#         gt_ext = 'csv', pred_ext = 'txt')
# method_type = 'azure'

# # log_and_print_entropy(root_dir, method_type, azure_matches2, azure_pth2, min_overlap_percentage, extra_verbose, verbose)

# ## Azure file 3
# azure_pth3 = root_dir.joinpath('EXP-002_Azure_IrmaTestSet3')

# azure_matches3 = matching_basename_pathlib_gt_pred(GT_pth, azure_pth3, 
#         gt_suffix_added='GT',
#         gt_ext = 'csv', pred_ext = 'txt')
# method_type = 'azure'

# # log_and_print_entropy(root_dir, method_type, azure_matches3, azure_pth3, min_overlap_percentage, extra_verbose, verbose)

# ## Azure all-together
# azure_all_pth = root_dir.joinpath('EXP-002_Azure_IrmaTestSet_all')

# azure_matches_all = matching_basename_pathlib_gt_pred(GT_pth, azure_all_pth, 
#         gt_suffix_added='GT',
#         gt_ext = 'csv', pred_ext = 'txt')
# method_type = 'azure'

# create_histogram(root_dir, method_type, azure_matches_all, cdf_flag=True)        



# ## Chunks_SHAS 
# ch_shas_pth = root_dir.joinpath('GT_AzureTestset_SHAS_Chunks_all_stages','final_csv')

# ch_shas_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_shas_pth, 
#         gt_suffix_added='GT', pred_suffix_added='pred',
#         gt_ext = 'csv', pred_ext = 'csv')
# method_type = 'Chunks_SHAS'

# log_and_print_entropy(root_dir, method_type, ch_shas_matches, ch_shas_pth, min_overlap_percentage, extra_verbose, verbose)
# create_histogram(root_dir, method_type, ch_shas_matches, cdf_flag=True)  


# ## Chunks Keppler mapper
# ch_TDA_pth = root_dir.joinpath('GT_AzureTestset_TDA_Chunks_all_stages','final_csv')

# ch_TDA_matches = matching_basename_pathlib_gt_pred(GT_pth, ch_TDA_pth, 
#         gt_suffix_added='GT', pred_suffix_added='pred',
#         gt_ext = 'csv', pred_ext = 'csv')
# method_type = 'Chunks_TDA'

# log_and_print_entropy(root_dir, method_type, ch_TDA_matches, ch_TDA_pth, min_overlap_percentage, extra_verbose, verbose)
# create_histogram(root_dir, method_type, ch_TDA_matches, cdf_flag=True)        


