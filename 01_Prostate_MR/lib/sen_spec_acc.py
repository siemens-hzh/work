from .lesion_valid import valid_lesion_detection
#import get_ground_truth
import pandas as pd
import numpy as np

from lesion_valid import lesion_distance

def case_cfm(pred_results, gt_results, threshold=3):

    tp, fp, tn, fn = [0, 0, 0, 0]
    for gt_key in gt_results.keys():
        cur_gt_score = gt_results[gt_key].case_score
        for pred_key in pred_results.keys():
            cur_pred_score = pred_results[pred_key].case_score
            if gt_key == pred_key:
                if cur_gt_score >= threshold:
                    if cur_pred_score >= threshold:
                        tp += 1
                    else:
                        fn += 1
                else:
                    if cur_pred_score < threshold:
                        tn += 1
                    else:
                        fp += 1
    recall = sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    precision =  tp / (tp + fp)
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    f1_score = 2 * recall * precision / (recall + precision)
    return [sensitivity, specificity, precision, accuracy, f1_score]

   
def lesion_cfm(pred_results, gt_results, threshold=3):
    tp, fp, fn, tn = [0, 0, 0, 0]
    for gt_key in gt_results:
        gt_lesions_info = gt_results[gt_key].lesions_info
        gt_selected_lesion = [x for x in gt_lesions_info if x.pirads_comb >= threshold]
        gt_lesion_count = len(gt_selected_lesion)
        for pred_key in pred_results:
            if gt_key == pred_key:
                cur_tp, cur_fn, cur_fp, cur_tn = [0, 0, 0, 0]
                pred_lesions_info = pred_results[pred_key].lesions_info
                pred_selected_lesion = [x for x in pred_lesions_info if x.pirads_comb >= threshold]
                pred_lesion_count = len(pred_selected_lesion)
                if gt_lesion_count == 0:
                    if pred_lesion_count > 0:
                        cur_fp = pred_lesion_count
                        fp += cur_fp
                        break
                    else:
                        cur_tn += 1
                        tn += cur_tn
                        break
                elif pred_lesion_count == 0:
                    cur_fn = pred_lesion_count
                    fn += cur_fn
                    break
                else:        
                    gt_lesion_status = [0 for idx in range(gt_lesion_count)]    
                    pred_lesion_status = [0 for idx in range(pred_lesion_count)]
                    for i in range(gt_lesion_count):
                        cur_gt_lesion_loc = gt_selected_lesion[i].location_mm
                        for j in range(pred_lesion_count):
                            if pred_lesion_status[j] == 1:
                                continue
                            cur_pred_lesion_loc = pred_selected_lesion[j].location_mm
                            if valid_lesion_detection(cur_gt_lesion_loc, cur_pred_lesion_loc):
                                gt_lesion_status[i] = 1
                                pred_lesion_status[j] = 1
                                continue
                        if gt_lesion_status[i] == 1:
                            continue
                    cur_tp += pred_lesion_status.count(1)
                    cur_fp += pred_lesion_status.count(0)
                    cur_fn += gt_lesion_status.count(0)
                    tp += cur_tp
                    fp += cur_fp
                    fn += cur_fn
                    break
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    precision = tp / (tp + fp)
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    return [sensitivity, specificity, precision, accuracy, 1]


def case_cfm2(pred_results, gt_results, threshold=3):
    # case_id, tp, fp, tn,fn
    results_list = []
    for gt_key in gt_results.keys():
        cur_gt_score = gt_results[gt_key].case_score
        for pred_key in pred_results.keys():
            cur_pred_score = pred_results[pred_key].case_score
            if gt_key == pred_key:
                result = [gt_key, 0,0,0,0]
                if cur_gt_score >= threshold:
                    if cur_pred_score >= threshold:
                        result[1] = 1
                    else:
                        result[4] = 1
                else:
                    if cur_pred_score < threshold:
                        result[3] = 1
                    else:
                        result[2] = 1
                results_list.append(result)
                break
    results_df = pd.DataFrame(results_list,columns=['Case_ID','TP','FP','TN','FN'])
    tp = sum(results_df['TP'])
    fp = sum(results_df['FP'])
    tn = sum(results_df['TN'])
    fn = sum(results_df['FN'])
    recall = sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    precision =  tp / (tp + fp)
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    f1_score = 2 * recall * precision /(precision + recall)
    return [results_df, sensitivity, specificity, precision, accuracy, f1_score]


def lesion_cfm2(pred_results, gt_results, threshold=3, distance=10):
    results_list = []
    for gt_key in gt_results:
        gt_lesions_info = gt_results[gt_key].lesions_info
        gt_selected_lesion = [x for x in gt_lesions_info if x.pirads_comb >= threshold]
        gt_lesion_count = len(gt_selected_lesion)
        for pred_key in pred_results:
            if gt_key == pred_key:
                #case_id, tp, fp, tn, fn
                result = [gt_key, 0, 0, 0, 0]
                pred_lesions_info = pred_results[pred_key].lesions_info
                pred_selected_lesion = [x for x in pred_lesions_info if x.pirads_comb >= threshold]
                pred_lesion_count = len(pred_selected_lesion)
                if gt_lesion_count == 0:
                    if pred_lesion_count > 0:
                        result[2] = pred_lesion_count
                    else:
                        result[3] = 1
                    results_list.append(result)
                    break
                elif pred_lesion_count == 0:
                    result[4] = gt_lesion_count
                    results_list.append(result)
                    break
                else:        
                    while(True):
                        gt_lesion_num = len(gt_selected_lesion)
                        pred_lesion_num = len(pred_selected_lesion)
                        cur_dist_m = np.zeros((gt_lesion_num, pred_lesion_num))
                        for i in range(gt_lesion_num):
                            cur_gt_lesion = gt_selected_lesion[i]
                            for j in range(pred_lesion_num):
                                cur_pred_lesion = pred_selected_lesion[j]
                                cur_dist_m[i,j] = lesion_distance(cur_pred_lesion, cur_gt_lesion)                         
                        cur_min_dist = np.min(cur_dist_m)
                        if cur_min_dist < distance:
                            result[1] += 1
                            cur_min_idx = np.where(cur_dist_m == cur_min_dist)
                            r_gt_idx, r_pred_idx = cur_min_idx[0][0], cur_min_idx[1][0]
                            gt_selected_lesion.pop(r_gt_idx)
                            pred_selected_lesion.pop(r_pred_idx)
                            if not len(gt_selected_lesion):
                                result[2] += len(pred_selected_lesion)
                                break
                            elif not len(pred_selected_lesion):
                                result[4] += len(gt_selected_lesion)
                                break
                        else:
                            result[2] += len(pred_selected_lesion)
                            result[4] += len(gt_selected_lesion)
                            break
                results_list.append(result)
    results_df = pd.DataFrame(results_list, columns=['Case_ID','TP','FP','TN','FN'])                
    tp = sum(results_df['TP'])
    #tn = sum(results_df['TN'])
    fp = sum(results_df['FP'])
    fn = sum(results_df['FN'])
    fp_rate = fp/(tp+fp)
    sensitivity = tp / (tp + fn)
    return [results_df, sensitivity, fp_rate]