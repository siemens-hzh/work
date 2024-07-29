import SimpleITK as sitk
from skimage.measure import label, regionprops


class gt_lesion_res:
    def __init__(self, image, gt_array, region):
        lesion_1st_pix = region.coords[0]
        self.pirads_comb = gt_array[lesion_1st_pix[0], lesion_1st_pix[1], lesion_1st_pix[2]]
        lesion_centroid = region.centroid[::-1]
        self.location_pix = [round(x) for x in lesion_centroid]
        self.location_mm = image.TransformIndexToPhysicalPoint(self.location_pix)

class gt_prostate_res:
    def __init__(self, case_name, label_file):
        self.patient_ID = case_name
        self.case_score = 1
        self.lesions_info = []
        self.lesion_gt(label_file)

    def lesion_gt(self,gt_file):
        image = sitk.ReadImage(gt_file)
        gt_array = sitk.GetArrayFromImage(image)
        labels, num = label(gt_array, connectivity=3, return_num=True)
        if num > 0:
            regions = regionprops(labels)
            for region in regions:
                lesion = gt_lesion_res(image, gt_array, region)
                self.lesions_info.append(lesion)    
                self.case_score = max(self.case_score, lesion.pirads_comb)