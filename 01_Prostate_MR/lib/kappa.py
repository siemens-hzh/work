from sklearn.metrics import cohen_kappa_score
from .lesion_valid import valid_lesion_detection

def lesion_kappa(pred_results, gt_results, weights_method='linear',threshold=3):
    gt_lesion_pirads = []
    pred_lesion_pirads = []
    corrected_count = 0
    for gt_key in gt_results:
        gt_lesions_info = gt_results[gt_key].lesions_info
        gt_selected_lesion = [x for x in gt_lesions_info if x.pirads_comb >= threshold]
        gt_lesion_count = len(gt_selected_lesion)
        for pred_key in pred_results:
            if gt_key == pred_key:
                pred_lesions_info = pred_results[pred_key].lesions_info
                pred_selected_lesion = [x for x in pred_lesions_info if x.pirads_comb >= threshold]
                pred_lesion_count = len(pred_selected_lesion)
                if gt_lesion_count == 0:
                    break
                elif pred_lesion_count == 0:
                    break
                else:
                    gt_lesion_status = [0] * len(gt_lesion_count)   
                    pred_lesion_status = [0] * len(pred_lesion_count)       
                    for i in range(gt_lesion_count):
                        cur_gt_lesion_loc = gt_selected_lesion[i].location_mm
                        cur_gt_lesion_pirads = gt_selected_lesion[i].pirads_comb
                        for j in range(pred_lesion_count):
                            if pred_lesion_status[j] == 1:
                                continue
                            cur_pred_lesion_loc = pred_selected_lesion[j].location_mm
                            cur_pred_lesion_pirads = pred_selected_lesion[j].pirads_comb
                            if valid_lesion_detection(cur_gt_lesion_loc, cur_pred_lesion_loc):
                                gt_lesion_pirads.append(cur_gt_lesion_pirads)
                                pred_lesion_pirads.append(cur_pred_lesion_pirads)
                                if cur_gt_lesion_pirads == cur_pred_lesion_pirads:
                                    corrected_count += 1
                                gt_lesion_status[i] = 1
                                pred_lesion_status[j] = 1
                                continue
                        if gt_lesion_status[i] == 1:
                            continue
                    break
    kappa_score = cohen_kappa_score(gt_lesion_pirads, pred_lesion_pirads, weights=weights_method)
    accuracy = corrected_count / len(pred_lesion_pirads)                
    return kappa_score, accuracy