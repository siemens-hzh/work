from .lesion_valid import valid_lesion_detection
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

def case_pirads_roc(pred_results, gt_results, threshold=3):
    gt_list = []
    pred_score_list = []
    for gt_key in gt_results.keys():
        gt_case_status = 1 if gt_results[gt_key].case_score >= threshold else 0
        for pred_key in pred_results.keys():
            if pred_key == gt_key:
                gt_list.append(gt_case_status)
                pred_score_list.append(pred_results[pred_key].los)
                break
    fpr,tpr,threshold = roc_curve(gt_list, pred_score_list)
    auc_score = auc(fpr, tpr)
    #plt.figure()
    lw = 2
    plt.figure(figsize=(10,10))
    plt.plot(fpr, tpr, color='darkorange',
            lw=lw, label='ROC curve (area = %0.4f)' % auc_score)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.savefig('ROC.png', bbox_inches='tight', dpi=450)
    #plt.show()
    return auc_score


def lesion_afroc(pred_results, gt_results, threshold=3):
    gt_list = []
    pred_score_list = []
    case_idx = 1
    negative_case_idx = []
    for pred_key in pred_results.keys():
        pred_lesions_info = pred_results[pred_key].lesions_info
        pred_lesion_list = [x for x in pred_lesions_info if x.pirads_comb >= threshold]
        for gt_key in gt_results.keys():
            if pred_key == gt_key:
                gt_lesions_info = gt_results[gt_key].lesions_info
                gt_lesion_list = [x for x in gt_lesions_info if x.pirads_comb >= threshold]
                if not len(gt_lesion_list):
                    negative_case_idx.append(case_idx)
                gt_lesion_count = len(gt_lesion_list)
                if len(pred_lesion_list) == 0:
                    if not gt_lesion_count:
                        pred_score_list.append([0, case_idx])
                        gt_list.append([0, case_idx])
                        break
                    else:
                        pred_score_list.extend([[0, case_idx] for i in range(gt_lesion_count)])
                        gt_list.extend([[1, case_idx] for i in range(gt_lesion_count)])
                        break
                for pred_lesion_info in pred_lesions_info:
                    flag = 0
                    cur_pred_lesion_loc = pred_lesion_info.location_mm
                    for gt_lesion_info in gt_lesions_info:
                        cur_gt_lesion_loc = gt_lesion_info.location_mm
                        if valid_lesion_detection(cur_pred_lesion_loc, cur_gt_lesion_loc):
                            gt_list.append([1, case_idx])
                            flag = 1
                            break
                    if not flag:
                        gt_list.append([0, case_idx])
                    pred_score_list.append([pred_lesion_info.los, case_idx])
                break
        case_idx += 1
    fpr, tpr = afroc_tpr_fpr(gt_list, pred_score_list, negative_case_idx)
    auc_score = afroc_auc(fpr, tpr)
    plt.figure()
    lw = 2
    plt.figure(figsize=(10,10))
    plt.plot(fpr, tpr, color='darkorange',
            lw=lw, label='AFROC curve (area = %0.4f)' % auc_score)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Case False Positive Rate')
    plt.ylabel('Lesion True Positive Rate')
    plt.title('Alternative Free-response Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.show()
    plt.savefig('pic1.jpg', bbox_inches='tight', dpi=450)
    return auc_score

def lesion_pirads_afroc(pred_results, gt_results):
    pass

def afroc_tpr_fpr(gt_label_list, pred_lesion_score_list, negative_case_idx):
    case_num = len(list(set([x[1] for x in gt_label_list])))
    negative_case_num = len(negative_case_idx)
    pred_lesion_num = len(pred_lesion_score_list)
    true_lesion_num = len([x for x in gt_label_list if x[0]==1])
    fpr_index  = [0, 100]
    case_fpr = []
    lesion_tpr = []
    for i in range(pred_lesion_num):
        if not gt_label_list[i][0] and pred_lesion_score_list[i][0]:
            fpr_index.append(pred_lesion_score_list[i][0])
    fpr_thres = sorted(list(set(fpr_index)), reverse=True)
    for thres in fpr_thres:
        lesion_tp = 0
        case_fp_status = [0 for i in range(case_num)]
        for i in range(pred_lesion_num-1):
            cur_case_idx = pred_lesion_score_list[i][1]
            if pred_lesion_score_list[i][0] >= thres:
                if gt_label_list[i][0]:
                    lesion_tp += 1
                else:
                    if cur_case_idx in negative_case_idx:
                        case_fp_status[cur_case_idx] |= 1
        cur_case_fp = case_fp_status.count(1)
        cur_lesion_tpr = lesion_tp / true_lesion_num
        cur_case_fpr = cur_case_fp / negative_case_num
        case_fpr.append(cur_case_fpr)
        lesion_tpr.append(cur_lesion_tpr)
    case_fpr.append(1)
    lesion_tpr.append(1)
    return case_fpr, lesion_tpr


def afroc_auc(fpr, tpr):
    afroc_auc = 0
    for i in range(len(fpr) - 1):
        cur_area = (tpr[i] + tpr[i+1]) * (fpr[i+1] - fpr[i]) / 2
        afroc_auc += cur_area
    return afroc_auc