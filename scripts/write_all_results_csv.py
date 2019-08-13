import argparse
import os
import sys

import pathlib
import torch
import pandas as pd

from src.uncertainty_measures import get_all_uncertainty_measures
from src.utils import get_interesting_result, write_dict_in_csv, get_file_and_dir_path_in_dir, convert_tensor_to_float

parser = argparse.ArgumentParser()
parser.add_argument('--polyaxon_results_path', help='path to polyaxon results', type=str)
parser.add_argument('--polyaxon_type', help='type of the experiments. Is either groups or experiments',
                    choices=['groups', 'experiments'], type = str, default='groups')
parser.add_argument('--group_nb', help='number of the group experiment if polyaxon_type is groups', type=str)
parser.add_argument('--exp_nb', help='number of the experiment if polyaxon_type is experiments',
                    type=str)
parser.add_argument('--which_file', help='which file to get from the folder of the output of the experiments.',
                    type=str, default='results')
parser.add_argument('--type_of_test', help='how is the test set compared to the training set',
                    choices=['random', 'unseen_classes', 'unseen_dataset'], type=str)
parser.add_argument('--extra_info', help='extra info to write on the name of the csv.', type=str,
                    default='')
args = parser.parse_args()

polyaxon_results_path = args.polyaxon_results_path
polyaxon_type = args.polyaxon_type
group_nb = args.group_nb
exp_nb = args.exp_nb
which_file = args.which_file
type_of_test = args.type_of_test
extra_info = args.extra_info

filename = pathlib.Path("results/raw_results/")
if group_nb is not None:
    _, all_dirs = get_file_and_dir_path_in_dir(os.path.join(polyaxon_results_path, polyaxon_type, group_nb), which_file)
    filename = filename / (str(group_nb) + str(extra_info))
elif exp_nb is not None:
    _, all_dirs = get_file_and_dir_path_in_dir(os.path.join(polyaxon_results_path, polyaxon_type, exp_nb), which_file)
    filename = filename / (str(exp_nb) + str(extra_info))

# results = []
# for file_path in all_dirs:
#     file_path = pathlib.Path(file_path)
#     result = torch.load(file_path / 'results.pt', map_location="cpu")
#
#     if type_of_test == 'random':
#         softmax_output = torch.load(file_path / 'softmax_outputs.pt', map_location='cpu')
#         seen_vr, seen_pe, seen_mi = get_all_uncertainty_measures(softmax_output)
#         result['seen uncertainty vr'] = seen_vr
#         result['seen uncertainty pe'] = seen_pe
#         result['seen uncertainty mi'] = seen_mi
#
#         random_output = torch.load(file_path / 'random_outputs.pt', map_location='cpu')
#         random_vr, random_pe, random_mi = get_all_uncertainty_measures(random_output)
#         result['random uncertainty vr'] = random_vr
#         result['random uncertainty pe'] = random_pe
#         result['random uncertainty mi'] = random_mi
#
#     elif type_of_test in ['unseen_classes', 'unseen_dataset']:
#         seen_output = torch.load(file_path / 'softmax_outputs_eval_seen.pt', map_location='cpu')
#         seen_vr, seen_pe, seen_mi = get_all_uncertainty_measures(softmax_output)
#         result['seen uncertainty vr'] = seen_vr
#         result['seen uncertainty pe'] = seen_pe
#         result['seen uncertainty mi'] = seen_mi
#
#         unseen_output = torch.load(file_path / 'softmax_outputs_eval_unseen.pt', map_location='cpu')
#         unseen_vr, unseen_pe, unseen_mi = get_all_uncertainty_measures(unseen_output)
#         result['unseen uncertainty vr'] = unseen_vr
#         result['unseen uncertainty pe'] = unseen_pe
#         result['unseen uncertainty mi'] = unseen_mi
#
#     results.append(get_interesting_result(result))
#     print(f'{len(results)} results loaded.')
# write_dict_in_csv(results, filename + '.csv')


results = pd.DataFrame()
for dir_path in all_dirs:
    dir_path = pathlib.Path(dir_path)
    result = pd.read_pickle(dir_path / 'results.pkl')
    if type_of_test == 'random':
        softmax_output = torch.load(dir_path / 'softmax_outputs.pt', map_location='cpu')
        seen_vr, seen_pe, seen_mi = get_all_uncertainty_measures(softmax_output)
        result['seen uncertainty vr'] = seen_vr
        result['seen uncertainty pe'] = seen_pe
        result['seen uncertainty mi'] = seen_mi

        random_output = torch.load(dir_path / 'random_outputs.pt', map_location='cpu')
        random_vr, random_pe, random_mi = get_all_uncertainty_measures(random_output)
        result['random uncertainty vr'] = random_vr
        result['random uncertainty pe'] = random_pe
        result['random uncertainty mi'] = random_mi

    elif type_of_test in ['unseen_classes', 'unseen_dataset']:
        seen_output = torch.load(dir_path / 'softmax_outputs_eval_seen.pt', map_location='cpu')
        seen_vr, seen_pe, seen_mi = get_all_uncertainty_measures(seen_output)
        result['seen uncertainty vr'] = seen_vr
        result['seen uncertainty pe'] = seen_pe
        result['seen uncertainty mi'] = seen_mi

        unseen_output = torch.load(dir_path / 'softmax_outputs_eval_unseen.pt', map_location='cpu')
        unseen_vr, unseen_pe, unseen_mi = get_all_uncertainty_measures(unseen_output)
        result['unseen uncertainty vr'] = unseen_vr
        result['unseen uncertainty pe'] = unseen_pe
        result['unseen uncertainty mi'] = unseen_mi

    results = results.append(result)
    print(f'{len(results)} results loaded.')

results = get_interesting_result(results)
convert_tensor_to_float(results)
results.to_csv(filename + '.csv')
results.to_pickle(filename + '.pkl')



