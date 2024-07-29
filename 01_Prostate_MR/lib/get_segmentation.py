import numpy as np

def extract_segment(img_data, label):
    img_data[img_data != label] = 0
    img_data[img_data == label] = 1
    return img_data

def compute_dice(pred_data, gt_data, digit=4):
    intersection = np.sum(pred_data * gt_data)
    dice = intersection * 2 / (np.sum(pred_data) + np.sum(gt_data))
    return round(dice, digit)
    