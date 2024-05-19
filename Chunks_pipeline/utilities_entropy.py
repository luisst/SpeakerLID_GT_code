import pprint
from scipy.stats import entropy
import numpy as np
import pandas as pd
import json

import matplotlib
import matplotlib.pyplot as plt

font = {'family' : 'monospace',
        'weight' : 'normal',
        'size'   : 17}
matplotlib.rc('font', **font)

def compute_histogram_bins(data, desired_bin_size):
    min_val = np.min(data)
    max_val = np.max(data)
    min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
    max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
    n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    return bins



def unpack_line(line, method_type):

    if method_type == 'azure':
        current_pred_label, \
        current_pred_start, \
        current_pred_end, \
        current_pred_text, \
        current_pred_prob = line.strip().split('\t')

    elif method_type == 'shas':
        current_wav_name, \
        current_pred_start, \
        current_pred_end = line.strip().split('\t')
        current_pred_label = 'Ignored'
    else:
        current_wav_name, \
        current_pred_label, \
        current_pred_start, \
        current_pred_end, \
        current_pred_duration = line.strip().split('\t')
    
    current_pred_start = float(current_pred_start)
    current_pred_end = float(current_pred_end)
    
    return current_wav_name, current_pred_label, current_pred_start, current_pred_end
    

def log_print(obj, pprint_flag = False, file='output_console.txt'):
        if pprint_flag:
                message = pprint.pformat(obj)
        else:
                message = str(obj) 

        print(message)
        with open(file, 'a') as f:
                f.write(message + '\n')


def plot_histograms(input_list_all, hist_path, method_type, desired_bin_size=1.0, cdf_flag=True):
        bins = compute_histogram_bins(np.array(input_list_all), desired_bin_size)     

        plt.figure(figsize=(10, 10))    
        n, output_bins, patches = plt.hist(x = input_list_all, bins=bins, color='#0504aa',
                                alpha=0.7, rwidth=0.85)

        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title(f'{method_type} - Length in seconds | Total: {len(input_list_all)}')
        plt.savefig(hist_path, dpi=300)

        if cdf_flag:
                cdf_hist_path = hist_path.parent.joinpath(f'CDF_{hist_path.name}.png')
                plt.figure(figsize=(10, 10))    
                n, output_bins2, patches = plt.hist(x = input_list_all, bins=bins, color='g',
                                                alpha=0.7, rwidth=0.85, cumulative=True)

                plt.grid(axis='y', alpha=0.75)
                plt.xlabel('Value')
                plt.ylabel('Frequency')
                plt.title(f'{method_type} - CDF Length | Total: {len(input_list_all)}')

                plt.savefig(cdf_hist_path, dpi=300)

        # plt.show()

def create_histogram(metric_output_folder,
                     method_type,
                     method_run_name,
                     ch_matches,
                     cdf_flag=True):
        current_date_time = pd.to_datetime('today').strftime('%Y-%m-%d_%H-%M')
        histogram_path = metric_output_folder.joinpath(f'Hist_{method_run_name}_{current_date_time}.png')

        length_lists = []

        for idx, current_match in enumerate(ch_matches):
                current_pred_csv_path = current_match[1]

                with open(current_pred_csv_path, 'r') as f:
                        Pred_lines = f.readlines()


                for prd_line_idx, current_pred_line in enumerate(Pred_lines):

                        current_wav_name, \
                        current_pred_label, \
                        current_pred_start, \
                        current_pred_end = unpack_line(current_pred_line, method_type)
                        length_lists.append(current_pred_end-current_pred_start)
                
        ## Plot the histogram
        desired_bin_size = 1.0 
        plot_histograms(length_lists, histogram_path, method_type, desired_bin_size, cdf_flag=cdf_flag)




def calculate_entropy(labels):
    value, counts = np.unique(labels, return_counts=True)
    probs = counts / len(labels)
    return entropy(probs, base=2)


def matched_to_print(current_pred_line, row_label, row_start, row_end, method_type):
        matched_to_print_tuple = ['','']
        
        _, current_pred_label, \
        current_pred_start, \
        current_pred_end = unpack_line(current_pred_line, method_type)

        matched_to_print_tuple[0] = f'{current_pred_label}\t{current_pred_start}\t{current_pred_end}' 
        matched_to_print_tuple[1] = f'{row_label}\t{row_start}\t{row_end}'
        return matched_to_print_tuple


def calculate_iou(predicted_start, predicted_end, gt_start, gt_end):
        intersection_start = max(predicted_start, gt_start)
        intersection_end = min(predicted_end, gt_end)

        intersection = max(0, intersection_end - intersection_start)
        union = max(predicted_end, gt_end) - min(predicted_start, gt_start)

        iou = intersection / union if union != 0 else 0
        return iou


def calculate_overlap_percentage(predicted_start, predicted_end, gt_start, gt_end):
        intersection_start = max(predicted_start, gt_start)
        intersection_end = min(predicted_end, gt_end)

        intersection = max(0, intersection_end - intersection_start)
        gt_size = gt_end - gt_start

        overlap_percentage = intersection / gt_size if gt_size != 0 else 0
        return overlap_percentage * 100  # Multiply by 100 to get the percentage


def calculate_metrics(current_pred_line, matched_segments_list, method_type): 
        current_wav_name, \
        current_pred_label, \
        current_pred_start, \
        current_pred_end = unpack_line(current_pred_line, method_type)


        matched_to_print_tuple = matched_to_print(current_pred_line, \
                                                        matched_segments_list[0][0],\
                                                        matched_segments_list[0][2],\
                                                        matched_segments_list[0][3],\
                                                        method_type)

        current_iou = calculate_iou(current_pred_start,\
                                                current_pred_end, \
                                                matched_segments_list[0][2], \
                                                matched_segments_list[0][3])
        overlap_GT_percentage =  calculate_overlap_percentage(current_pred_start,\
                                                current_pred_end, \
                                                matched_segments_list[0][2], \
                                                matched_segments_list[0][3])
        return current_iou, overlap_GT_percentage, matched_to_print_tuple


def match_segments(current_pred_line, df_GT, method_type, mylog, min_overlap_percentage, extra_verbose):
        
        current_wav_name, \
        current_pred_label, \
        current_pred_start, \
        current_pred_end = unpack_line(current_pred_line, method_type)

        matched_segments_list = []

        no_overlap_count = 0
        no_overlap_seconds = 0.0

        for index, row in df_GT.iterrows():
                start_time = float(row['start_time'])
                end_time = float(row['end_time'])
                
                overlap = max(0, min(current_pred_end, end_time) - max(current_pred_start, start_time))
                overlap_percentage = overlap / (current_pred_end - current_pred_start)
                
                if overlap_percentage > min_overlap_percentage:
                        matched_segments_list.append((row['label'], round(overlap_percentage,2), start_time, end_time))
                else:
                        ## Count predicitons that do not overlap with any GT
                        no_overlap_count += 1
                        no_overlap_seconds += current_pred_end - current_pred_start

                        if extra_verbose:
                                row_label = row['label']
                                row_start = row['start_time']
                                row_end = row['end_time']
                                matched_to_print_tuple = matched_to_print(current_pred_line, row_label, row_start, row_end, method_type) 
                                log_print(f'\n\t{index}-No overlap between', file=mylog)
                                log_print(f'\t{matched_to_print_tuple[0]}\n\t{matched_to_print_tuple[1]}', file=mylog)

        matched_segments_list.sort(key=lambda x: x[1], reverse=True)

        no_overlap_tuple = (no_overlap_count, no_overlap_seconds)
        return matched_segments_list, no_overlap_tuple


def print_metrics_summary(IOU_list, overlap_GT_list, mylog): 
        ## Calculate the average IOU and overlap percentage
        average_IOU = sum(IOU_list) / len(IOU_list)
        average_overlap_percentage = sum(overlap_GT_list) / len(overlap_GT_list)
        log_print(f'average_IOU: {average_IOU:.2f} \t average_overlap_percentage: {average_overlap_percentage:.2f}%', file=mylog)

        ## Print the percentage of of 0.0 in the IOU and overlap_GT_list
        percentage_zeros_IOU = (IOU_list.count(0.0) / len(IOU_list)) * 100
        percentage_zeros_overlap_GT = (overlap_GT_list.count(0.0) / len(overlap_GT_list)) * 100
        log_print(f'percentage_zeros_IOU: {percentage_zeros_IOU:.2f}% \t percentage_zeros_overlap_GT: {percentage_zeros_overlap_GT:.2f}%', file=mylog)


def print_entropy_details(session_dict, mylog, extra_heading=''):

        log_print(f'\n{extra_heading}', file=mylog)
        log_print('\nSession dict:', file=mylog)
        for key, current_value in session_dict.items():
                element_count = {}
                for element in current_value:
                        if element in element_count:
                                element_count[element] += 1
                        else:
                                element_count[element] = 1
                log_print(f'Pred {key}', file=mylog)
                log_print(element_count, pprint_flag=True, file=mylog)

        for key, current_value in session_dict.items():
                entropy_value = calculate_entropy(current_value)
                log_print(f'\tEntropy {key}:  {entropy_value:.3f}', file=mylog)


def generate_IOU_overlap_lists(session_dict, paths_dicts,
                               matched_segments_list,
                               current_pred_line,
                               method_type,
                               mylog,
                               prd_line_idx,
                               json_path,
                               verbose=False):

        current_wav_name, \
        current_pred_label, \
        current_pred_start, \
        current_pred_end = unpack_line(current_pred_line, method_type)

        IOU_list = []
        overlap_GT_list = []

        if len(matched_segments_list) > 0:
                current_iou, \
                overlap_GT_percentage, \
                matched_to_print_tuple = calculate_metrics(current_pred_line,
                                                           matched_segments_list,\
                                                           method_type)
                IOU_list.append(current_iou)
                overlap_GT_list.append(overlap_GT_percentage)

                current_GT_label = matched_segments_list[0][0]

                if current_pred_label in session_dict:
                        session_dict[current_pred_label].append(current_GT_label)
                else:
                        session_dict[current_pred_label] = [current_GT_label]
                
                if current_pred_label in paths_dicts:
                        paths_dicts[current_pred_label].append((current_wav_name, current_GT_label))
                else:
                        paths_dicts[current_pred_label] = [(current_wav_name, current_GT_label)]
                
                if verbose:
                        if len(matched_segments_list) >= 3:
                                log_print(f'\n{prd_line_idx}-current_pred_line: {current_pred_line.strip()}', file=mylog)
                                log_print(f'Found 3 matches:', file=mylog)
                                log_print(matched_segments_list[:3], file=mylog)
                        elif len(matched_segments_list) == 2:
                                log_print(f'\n{prd_line_idx}-current_pred_line: {current_pred_line.strip()}', file=mylog)
                                log_print(f'Found 2 matches:', file=mylog)
                                log_print(matched_segments_list[:2], file=mylog)
                        else:
                                log_print(f'\n{prd_line_idx}-current_pred_line:')
                                log_print(f'One match score:{matched_segments_list[0][1]}  -   IoU: {current_iou:.2f}   -   Overlap GT: {overlap_GT_percentage:.2f}%', file=mylog)
                                log_print(f'{matched_to_print_tuple[0]}\n{matched_to_print_tuple[1]}', file=mylog)
        else:
                if verbose:
                        log_print(f'\n{prd_line_idx}-current_pred_line: {current_pred_line.strip()}', file=mylog)
                        log_print(f'\tNo matches found', file=mylog)
                IOU_list.append(0.0)
                overlap_GT_list.append(0.0)

                if current_pred_label in session_dict:
                        session_dict[current_pred_label].append('Other_Speaker')
                else:
                        session_dict[current_pred_label] = ['Other_Speaker']       
                
                if current_pred_label in paths_dicts:
                        paths_dicts[current_pred_label].append((current_wav_name, 'Other_Speaker'))
                else:
                        paths_dicts[current_pred_label] = [(current_wav_name, 'Other_Speaker')]
                
        with open(json_path, 'w') as json_file:
                json.dump(paths_dicts, json_file)

        return IOU_list, overlap_GT_list, session_dict, paths_dicts


def log_and_print_entropy(metric_output_folder,
                          method_type,
                          run_name,
                          run_params,
                          ch_matches,
                          min_overlap_percentage,
                          extra_verbose,
                          verbose):
        current_date_time = pd.to_datetime('today').strftime('%Y-%m-%d_%H-%M')
        mylog = str(metric_output_folder.joinpath(f'Entropy_{run_name}_{current_date_time}.txt'))
        json_path = metric_output_folder.joinpath(f'session_dict.json')

        session_dict = {}
        paths_dicts = {}

        log_print(f'Entropy for {method_type}', file=mylog)

        for idx, current_match in enumerate(ch_matches):
                current_GT_csv_path = current_match[0]
                current_pred_csv_path = current_match[1]
                df_GT = pd.read_csv(current_GT_csv_path, sep='\t', names=['label', 'lang', 'start_time', 'end_time'])

                # Print current pred csv path
                log_print(f'\n\n      {idx} - current_pred_csv_path: {current_pred_csv_path.name}', file=mylog)

                with open(current_pred_csv_path, 'r') as f:
                        Pred_lines = f.readlines()

                ## Count how many seconds in total from all prediction lines
                total_pred_seconds = 0.0
                for current_pred_line in Pred_lines:
                        current_wav_name, \
                        current_pred_label, \
                        current_pred_start, \
                        current_pred_end = unpack_line(current_pred_line, method_type)
                        total_pred_seconds += current_pred_end - current_pred_start

                ## Count how many seconds in total from all GT lines
                total_GT_seconds = 0.0
                for index, row in df_GT.iterrows():
                        total_GT_seconds += row['end_time'] - row['start_time']


                for prd_line_idx, current_pred_line in enumerate(Pred_lines):

                    current_wav_name, \
                    current_pred_label, \
                    current_pred_start, \
                    current_pred_end = unpack_line(current_pred_line, method_type)

                    matched_segments_list, no_overlap_tuple = match_segments(current_pred_line, df_GT,\
                                                           method_type, mylog, \
                                                    min_overlap_percentage, extra_verbose)

                    IOU_list, overlap_GT_list, \
                        session_dict, paths_dicts = generate_IOU_overlap_lists(session_dict, \
                                                                                paths_dicts, \
                                                                                matched_segments_list, \
                                                                                current_pred_line, \
                                                                                method_type, \
                                                                                mylog, \
                                                                                prd_line_idx, \
                                                                                json_path, \
                                                                                verbose=False)

                if verbose:
                        log_print(f'\n\nIOU_list:', file=mylog)
                        log_print([round(i, 2) for i in IOU_list], pprint_flag=True, file=mylog)
                        log_print(f'overlap_GT_list:', file=mylog)
                        log_print([round(i, 2) for i in overlap_GT_list], pprint_flag=True, file=mylog)


                ## Print the summary of the metrics for IOU and overlap_GT_list
                print_metrics_summary(IOU_list, overlap_GT_list, mylog)


        ## Print the entropy details of the session_dict
        print_entropy_details(session_dict, mylog)

        print_entropy_details(paths_dicts, mylog, extra_heading='PATHS DICTS')

        # Print the average entropy of the session_dict
        entropy_values = [calculate_entropy(current_value) for current_value in session_dict.values()]

        average_entropy = sum(entropy_values) / len(entropy_values)
        log_print(f'\nAverage {method_type} entropy: {average_entropy:.3f}', file=mylog)

        log_print(f'---------------------------------------', file=mylog)
        log_print(f'Count no-overlap: {no_overlap_tuple[0]}', file=mylog)
        log_print(f'Seconds no-overlap: {no_overlap_tuple[1]:.2f}s', file=mylog)

        # Calculate the percentage of no-overlap seconds
        no_overlap_percentage = (no_overlap_tuple[1] / total_pred_seconds) * 100
        log_print(f'Percentage no-overlap: {no_overlap_percentage:.2f}% \t Total Pred: {total_pred_seconds:.2f}', file=mylog)

        # Calculate the percentage of no-overlap seconds from the total GT seconds
        no_overlap_percentage_GT = (no_overlap_tuple[1] / total_GT_seconds) * 100
        log_print(f'Percentage no-overlap GT: {no_overlap_percentage_GT:.2f}% \t Total GT: {total_GT_seconds:.2f}', file=mylog)

        log_print(f'---------------------------------------', file=mylog)

        log_print(f'Run Method: {method_type}', file=mylog)
        log_print(f'Run Name: {run_name}', file=mylog)
        log_print(f'Run Params: {run_params}', file=mylog)
    

