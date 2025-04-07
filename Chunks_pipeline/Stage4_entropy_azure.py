
from pathlib import Path
import argparse
import os
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred
from utilities_entropy import log_and_print_entropy, create_histogram, single_pred


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
parser.add_argument('--run_name', default='default_name', help='Run ID name')
parser.add_argument('--run_params', default='default_params', help='Run ID name')


args = parser.parse_args()

csv_pred_folder = args.csv_pred_folder
GT_csv_folder = args.GT_csv_folder
metric_output_folder = args.metric_output_folder
pred_suffix_added = args.pred_suffix
pred_ext = args.pred_extensions
min_overlap_percentage = float(args.min_overlap_pert)
run_name = args.run_name
run_params = args.run_params

if pred_suffix_added == 'xx':
    pred_suffix_added = ''
    print('updating pred_suffix_added to empty string')

print(f'>>>>>>> pred_suffix: {pred_suffix_added} \t ext: {pred_ext}')

print(f'Metrics folder: {metric_output_folder}')


suffix_ext_list = [pred_ext, pred_suffix_added]

# print elements in suffix_ext_list
print(f' main suffix: {suffix_ext_list[1]} \t main ext: {suffix_ext_list[0]}')

verbose = False
extra_verbose = False
#### ---------------------- ####

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
                    'azure',
                    current_azure_run,
                    run_params,
                    suffix_ext_list,
                    verbose=verbose,
                    extra_verbose=extra_verbose,
                    min_overlap_percentage=min_overlap_percentage)
    else:
        print(f'WARNING!!! \t {azure_part_folder} is not a folder')