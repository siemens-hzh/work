import numpy as np
from scipy.spatial.distance import pdist

def valid_lesion_detection(pred_loc, gt_loc, distance_threshold=10):
    pred_pt = np.array(pred_loc)
    gt_pt = np.array(gt_loc)
    dist_matrix = np.vstack((pred_pt, gt_pt))
    distance = pdist(dist_matrix, 'euclidean')
    return True if distance <= distance_threshold else False

def valid_pirads_score(pred_score, gt_score):
    return True if pred_score == gt_score else False


def lesion_distance(pred_lesion, gt_lesion):
    pred_loc = pred_lesion.location_mm
    gt_loc = gt_lesion.location_mm
    #print(gt_lesion.location_pix, gt_loc)
    pred_pt = np.array(pred_loc)
    gt_pt = np.array(gt_loc)
    dist_matrix = np.vstack((pred_pt, gt_pt))
    dist = pdist(dist_matrix, 'euclidean')
    return dist