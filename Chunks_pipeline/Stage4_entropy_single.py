from pathlib import Path
import argparse
import os
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred
from utilities_entropy import log_and_print_entropy, create_histogram


def single_pred(csv_pred_folder, 
                GT_csv_folder,
                metric_output_folder,
                method_type,
                run_name,
                run_params,
                suffix_ext_list,
                verbose=False,
                extra_verbose=False,
                min_overlap_percentage=0.3):

    verbose = False
    extra_verbose = False

    print(f'suffix: {suffix_ext_list[1]} \t ext: {suffix_ext_list[0]}')

    method_matches = matching_basename_pathlib_gt_pred(GT_csv_folder, csv_pred_folder, 
            gt_suffix_added='GT', pred_suffix_added=suffix_ext_list[1],
            gt_ext = 'csv', pred_ext = suffix_ext_list[0])
    
    print(f'>>> method_matches:\n{method_matches}')

    log_and_print_entropy(metric_output_folder,
                          method_type,
                          run_name,
                          run_params,
                          method_matches,
                          min_overlap_percentage,
                          extra_verbose,
                          verbose)

    create_histogram(metric_output_folder,
                     method_type,
                     run_name,
                     method_matches,
                     cdf_flag=True)        


def azure_multiple_wavs(csv_pred_folder, 
                        GT_csv_folder,
                        metric_output_folder,
                        method_type,
                        run_name,
                        suffix_ext_list,
                        verbose=False,
                        extra_verbose=False,
                        min_overlap_percentage=0.3):


    # Read all txt files in the method_folder
    all_azure_files = list(csv_pred_folder.glob('**/*.txt'))

    # Check if there are files in the folder
    if len(all_azure_files) == 0:
        print(f'WARNING!!! \t No files found in {csv_pred_folder}')

    # Iterate over all folders in the method_folder
    for azure_part_folder in csv_pred_folder.iterdir():
        if azure_part_folder.is_dir():
            current_azure_run = f'{run_name}-{azure_part_folder.stem}'

            print(f'>>> inside Azure folder: {azure_part_folder}')

            single_pred(azure_part_folder, 
                        GT_csv_folder,
                        metric_output_folder,
                        method_type,
                        current_azure_run,
                        'azureV3.1',
                        suffix_ext_list,
                        verbose=verbose,
                        extra_verbose=extra_verbose,
                        min_overlap_percentage=min_overlap_percentage)
        else:
            print(f'WARNING!!! \t {azure_part_folder} is not a folder')


def run_single_pred(csv_pred_folder, 
                    GT_csv_folder,
                    metric_output_folder,
                    method_type,
                    run_name,
                    run_params,
                    suffix_ext_list,
                    verbose=False,
                    extra_verbose=False,
                    min_overlap_percentage=0.3):

    if (method_type == 'azure'):
        print(f'\nRunning Azure method')
        azure_multiple_wavs(csv_pred_folder, 
                            GT_csv_folder,
                            metric_output_folder,
                            method_type,
                            run_name,
                            suffix_ext_list,
                            verbose=verbose,
                            extra_verbose=extra_verbose,
                            min_overlap_percentage=min_overlap_percentage)
    else:
        print(f'\nRunning OUR method')
        single_pred(csv_pred_folder, 
                    GT_csv_folder,
                    metric_output_folder,
                    method_type,
                    run_name,
                    run_params,
                    suffix_ext_list,
                    verbose=verbose,
                    extra_verbose=extra_verbose,
                    min_overlap_percentage=min_overlap_percentage)


def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','')
csv_pred_folder_ex = base_path_ex.joinpath('')
GT_csv_folder_ex = base_path_ex.joinpath('')
metric_output_folder_ex = base_path_ex.joinpath('')

parser = argparse.ArgumentParser()

parser.add_argument('--csv_pred_folder', type=valid_path, default=csv_pred_folder_ex, help='Initial WAVs folder path')
parser.add_argument('--GT_csv_folder', type=valid_path, default=GT_csv_folder_ex, help='Prediction with folders per label')
parser.add_argument('--metric_output_folder', type=valid_path, default=metric_output_folder_ex, help='Separated per Long wav folder path')
parser.add_argument('--pred_suffix', default='prd', help='Suffix added to the prediction files')
parser.add_argument('--pred_extensions', default='csv', help='extension of the prediction files')
parser.add_argument('--min_overlap_pert', default=0.3, help='Minimum overlap percentage for the metric calculation')
parser.add_argument('--method_name', default='default_method', help='Method name, Azure or Others')
parser.add_argument('--run_name', default='default_name', help='Run ID name')
parser.add_argument('--run_params', default='default_params', help='Run ID name')


args = parser.parse_args()

csv_pred_folder = args.csv_pred_folder
GT_csv_folder = args.GT_csv_folder
metric_output_folder = args.metric_output_folder
pred_suffix_added = args.pred_suffix
pred_ext = args.pred_extensions
min_overlap_percentage = float(args.min_overlap_pert)
method_type = args.method_name
run_name = args.run_name
run_params = args.run_params

if pred_suffix_added == 'xx':
    pred_suffix_added = ''
    print('updating pred_suffix_added to empty string')

print(f'>>>>>>> pred_suffix: {pred_suffix_added} \t ext: {pred_ext}')

print(f'Metrics folder: {metric_output_folder}')

method_type = method_type.lower()

suffix_ext_list = [pred_ext, pred_suffix_added]

# print elements in suffix_ext_list
print(f' main suffix: {suffix_ext_list[1]} \t main ext: {suffix_ext_list[0]}')


# methods_dict = {'Chunks_SHAS': {'pred_suffix_added':'pred', 'pred_ext':'csv'},
#                 'Chunks_TDA': {'pred_suffix_added':'pred', 'pred_ext':'csv'},
#                 'azure': {'pred_suffix_added':'', 'pred_ext':'txt'}}

verbose = False
extra_verbose = False
#### ---------------------- ####

run_single_pred(csv_pred_folder, 
            GT_csv_folder,
            metric_output_folder,
            method_type,
            run_name,
            run_params,
            suffix_ext_list,
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


