import os
import SimpleITK as sitk
import numpy as np

def generate_gt(reader_list, case_list, root_folder):
    
    '''
    Function usage: 
        To generate ground truth from n experts' annotation by majority voting method
    Parameters:
        reader_list: Annotator's name list(folder list)
        case_list: Annotated case list
        root_folder: The annotation root folder
    Returns:
        The validation result(which case not fully annoatated)
    '''

    validation_list = []
    reader_num = len(reader_list)
    majority_num = int(reader_num / 2) + 1
    for case_name in case_list:
        output_folder = os.path.join(root_folder, case_name, 'gt')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        masks = [0] * reader_num
        bmasks = [0] * reader_num
        for i in range(reader_num):
            cur_mask = os.path.join(root_folder, reader_list[i], case_name, case_name + '.mhd')
            mask_img = sitk.ReadImage(cur_mask)
            img_array = sitk.GetArrayFromImage(mask_img)
            if np.max(img_array) == 255:
                validation_list.append([reader_list[i], case_name])
            masks[i] = sitk.GetArrayFromImage(mask_img)
            img_array[img_array > 1] = 1
            bmasks[i] = img_array
        bmask = bmasks[0] + bmasks[1] + bmasks[2]
        z_max, x_max, y_max = img_array.shape
        gt_array = np.zeros(img_array.shape, dtype=np.uint8)
        for z in range(z_max):
            for x in range(x_max):
                for y in range(y_max):
                    if bmask[z, x, y] >= majority_num:
                        gt_array[z, x, y] = sorted([masks[0][z, x, y],masks[1][z, x, y],masks[2][z, x, y]])[majority_num]
        gt_img = sitk.GetImageFromArray(gt_array)
        sitk.WriteImage(gt_img, os.path.join(output_folder,'m0.mhd'))
    return validation_list                