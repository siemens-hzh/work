
import os, copy
import SimpleITK as sitk
import numpy as np
from skimage import measure

import SimpleITK as sitk


def get_bin_label(merge_input, reader_list, case):
    bin_list = []
    label_list = []
    uncompleted_list = []
    for i in range(len(reader_list)):
        cur_image = sitk.ReadImage(os.path.join(merge_input, reader_list[i], case, case+'.mhd'))
        cur_origin = cur_image.GetOrigin()
        cur_spacing = cur_image.GetSpacing()
        cur_img = sitk.GetArrayFromImage(cur_image)
        if np.max(cur_img) == 255:
            uncompleted_list.append(reader_list[i])
        cur_shape = cur_img.shape
        cur_label = copy.deepcopy(cur_img)
        cur_img[cur_img>0]=1
        bin_list.append(cur_img)
        label_list.append(cur_label)
    return bin_list, label_list, cur_shape, uncompleted_list, cur_origin, cur_spacing


def merge_annotation(bin_list, label_list, image_shape,threshold=2):
    if threshold == 1:
        single_anno = True
    else:
        single_anno = False
    sum_array = np.zeros(image_shape).astype(np.uint8)
    for bin in bin_list:
        sum_array = np.add(sum_array, bin)
    bin_array = copy.deepcopy(sum_array)    
    bin_array[bin_array<threshold] = 0
    bin_array[bin_array>=threshold] = 1
    labels = measure.label(bin_array, connectivity=3)
    props = measure.regionprops(labels)
    end_flag = False
    pirads_array = np.zeros(image_shape).astype(np.uint8)
    for prop in props:
        cur_comp_coords = prop.coords     
        for coord in cur_comp_coords:
            z,y,x = coord
            if sum_array[z,y,x] == 3:
                cur_comp_score = majority_vote(label_list,coord)
                end_flag = True
                break
        if not end_flag:
            for coord in cur_comp_coords:
                z,y,x = coord
                if sum_array[z,y,x] == 2:
                    cur_comp_score = majority_vote(label_list,coord)
                    end_flag = True
                    break
        if not end_flag:
            coord = cur_comp_coords[0]
            cur_comp_score = majority_vote(label_list, coord, single_anno)
            end_flag = True
        for coord in cur_comp_coords:
            z,y,x = coord
            pirads_array[z,y,x] = cur_comp_score
    return pirads_array


def majority_vote(label_list, coord, single_anno=False):
    z,y,x = coord
    pirads_list = []
    for label in label_list:
        pirads_list.append(label[z,y,x])
    if single_anno:
        pirads_score = max(pirads_list)
    else:
        pirads_score = sorted(pirads_list)[1]
    return pirads_score


def save_merge(data, origin,spacing, output_folder):
    output_image = sitk.GetImageFromArray(data)
    output_image.SetOrigin(origin)
    output_image.SetSpacing(spacing)
    output_path = os.path.join(output_folder, 'm0.mhd')
    sitk.WriteImage(output_image, output_path)
    return True