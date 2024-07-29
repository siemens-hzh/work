import re
import os

from skimage.measure import label, regionprops
import SimpleITK as sitk

class pred_lesion_res:
    def __init__(self, content):
        self.location_pix = self.get_result(content[0])
        self.location_mm = self.get_result(content[1], False)
        self.sectional_measurement_pt1 = self.get_result(content[2], False)
        self.sectional_measurement_pt2 = self.get_result(content[3], False)
        self.sectional_diameter = self.get_result(content[4], False)
        self.largest_measurement_pt1 = self.get_result(content[5], False)
        self.largest_measurement_pt2 = self.get_result(content[6], False)
        self.largest_diameter = self.get_result(content[7], False)
        self.pirads_comb = self.get_result(content[8])
        self.los = self.get_result(content[9])
        self.median_adc = self.get_result(content[10])
        self.ten_percentile_adc = self.get_result(content[11])
        self.anatomy = self.get_result(content[12])
        self.laterality = self.get_result(content[13])
        self.region = self.get_result(content[14])
        self.zone = self.get_result(content[15])

    def get_result(self, content, integer=True):
        res_string = content.split('= ')[1]
        temp = re.findall(r'-?\d+\.?\d*', res_string)
        if len(temp) > 1:
            if integer:
                return [int(x) for x in temp]
            else:
                return [float(x) for x in temp]
        elif len(temp) == 1:
            if integer:
                return int(temp[0])
            else:
                return float(temp[0])
        else:
            return res_string

class pred_prostate_res:
    def __init__(self,id):
        self.patient_ID = id
        self.lesion_number = 0
        self.lesions_info = []
        self.los = 0
        self.case_score = 1

    def extract_findings(self, lesion_file):
        with open(lesion_file, 'r') as f:
            content = f.read()
        self.lesion_number = content.count('#')
        lesions_content = content.split('#')[1:]
        for lesion_content in lesions_content:
            lesion_info = pred_lesion_res(lesion_content.split('\n')[1:])
            self.lesions_info.append(lesion_info)
        self.get_prostate_score()

    def get_prostate_score(self):
        for lesion_info in self.lesions_info:
            self.case_score = max(self.case_score, lesion_info.pirads_comb)



class pred_lesion_res2:
    def __init__(self, index, content, lesion_mask):
        self.lesion_index = index
        self.location_pix, self.location_mm = self.get_lesion_location(lesion_mask)
        #self.location_pix = self.get_result(content[0])
        #self.location_mm = self.get_result(content[1], False)
        self.sectional_measurement_pt1 = self.get_result(content[2], False)
        self.sectional_measurement_pt2 = self.get_result(content[3], False)
        self.sectional_diameter = self.get_result(content[4], False)
        self.largest_measurement_pt1 = self.get_result(content[5], False)
        self.largest_measurement_pt2 = self.get_result(content[6], False)
        self.largest_diameter = self.get_result(content[7], False)
        self.pirads_comb = self.get_result(content[8])
        self.los = self.get_result(content[9])
        self.median_adc = self.get_result(content[10])
        self.ten_percentile_adc = self.get_result(content[11])
        self.anatomy = self.get_result(content[12])
        self.laterality = self.get_result(content[13])
        self.region = self.get_result(content[14])
        self.zone = self.get_result(content[15])        

    def get_result(self, content, integer=True):
        res_string = content.split('= ')[1]
        temp = re.findall(r'-?\d+\.?\d*', res_string)
        if len(temp) > 1:
            if integer:
                return [int(x) for x in temp]
            else:
                return [float(x) for x in temp]
        elif len(temp) == 1:
            if integer:
                return int(temp[0])
            else:
                return float(temp[0])
        else:
            return res_string
        
    def get_lesion_location(self, mask):
        image = sitk.ReadImage(mask)
        lesion_array = sitk.GetArrayFromImage(image)
        labels = label(lesion_array, connectivity=3)
        regions = regionprops(labels)
        for region in regions:
            lesion_centroid = region.centroid[::-1]
            location_pix = [round(x) for x in lesion_centroid]
            location_mm = image.TransformIndexToPhysicalPoint(location_pix)
        return location_pix, location_mm 


class pred_prostate_res2:
    def __init__(self,id):
        self.patient_ID = id
        self.lesion_number = 0
        self.lesions_info = []
        self.los = 0
        self.case_score = 1

    def extract_findings(self, lesion_file):
        with open(lesion_file, 'r') as f:
            content = f.read()
        self.lesion_number = content.count('#')
        lesions_content = content.split('#')[1:]
        for lesion_content in lesions_content:
            lesion_idx = lesion_content.split('\n')[0]
            lesion_mask = os.path.join(os.path.dirname(lesion_file), 'lesion_' + lesion_idx +'.mhd')
            lesion_info = pred_lesion_res2(lesion_idx, lesion_content.split('\n')[1:], lesion_mask)
            self.lesions_info.append(lesion_info)
        self.get_prostate_score()
            
    def get_prostate_score(self):
        for lesion_info in self.lesions_info:
            self.case_score = max(self.case_score, lesion_info.pirads_comb)
            
    def get_lesion_loccation(self, mask_file):
        image = sitk.ReadImage(mask_file)
        lesion_array = sitk.GetArrayFromImage(image)
        labels = label(lesion_array, connectivity=3)

        regions = regionprops(labels)
        for region in regions:
            lesion_centroid = region.centroid[::-1]
            location_pix = [round(x) for x in lesion_centroid]
            location_mm = image.TransformIndexToPhysicalPoint(self.location_pix)
        return location_pix, location_mm 