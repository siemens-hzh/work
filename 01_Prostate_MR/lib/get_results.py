import os

from .get_gt_results import gt_prostate_res
from .result_extraction import pred_prostate_res
from .result_extraction import pred_prostate_res2



def batch_gt_results(gt_root,gt_folder_name):
    gt_dict = dict()
    gt_cases_list = os.listdir(gt_root)
    for case_folder in gt_cases_list:
        gt_folder = os.path.join(gt_root, case_folder, gt_folder_name)
        gt_files_list = os.listdir(gt_folder)
        for file in gt_files_list:
            if file.endswith('.mhd'):
                gt_info = gt_prostate_res(case_folder, os.path.join(gt_folder, file))
                gt_dict.setdefault(case_folder, gt_info)
                break 
    return gt_dict  

def batch_pred_results(pred_root):
    pred_dict = dict()
    pred_cases_list = os.listdir(pred_root)
    for case_folder in pred_cases_list:
        prostate_result = pred_prostate_res(case_folder)
        if case_folder in ['_html_reports', '_logs']:
            continue
        else:
            for root, _, files in os.walk(os.path.join(pred_root, case_folder)):
                for file in files:
                    if file == 'caseLevelLoS.txt':
                        with open(os.path.join(root,file), 'r') as f:
                            prostate_result.los = float(f.read())
                    if file == 'LesionFindings.txt':
                        prostate_result.extract_findings(os.path.join(root, file))
        pred_dict.setdefault(case_folder, prostate_result)
    return pred_dict


def batch_pred_results2(pred_root):
    pred_dict = dict()
    pred_cases_list = os.listdir(pred_root)
    for case_folder in pred_cases_list:
        prostate_result = pred_prostate_res2(case_folder)
        if case_folder in ['_html_reports', '_logs']:
            continue
        else:
            for root, _, files in os.walk(os.path.join(pred_root, case_folder)):
                for file in files:
                    if file == 'caseLevelLoS.txt':
                        with open(os.path.join(root,file), 'r') as f:
                            prostate_result.los = float(f.read())
                    if file == 'LesionFindings.txt':
                        prostate_result.extract_findings(os.path.join(root, file))
        pred_dict.setdefault(case_folder, prostate_result)
    return pred_dict