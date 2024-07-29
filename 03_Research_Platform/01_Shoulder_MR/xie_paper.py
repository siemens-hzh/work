import math
import SimpleITK as sitk
import numpy as np
import pandas as pd
import seaborn as sns

mask_file = r'C:\Users\z004b0je\OneDrive - Siemens Healthineers\Projects\20_Scientific_Proof_Points\huashan_LLM\xie.nii.gz'
image_dicom = r'C:\Users\z004b0je\Downloads\腰椎DIXON-axi\腰椎DIXON-axi\术后Dixon\Q-Dixon (axi)_FF_205938_29\00000043.dcm'

mask_image = sitk.ReadImage(mask_file)
image = sitk.ReadImage(image_dicom)
spacing = image.GetSpacing()
size = image.GetSize()

def circle_coordinates(center_x,center_y, radius):
    theta = 0.0
    increment = 0.01 
    coordinates =[]
    while theta < 2 * math.pi:
        x=round(center_x + radius * math.cos(theta))
        y=round(center_y+ radius * math.sin(theta))
        coordinates.append((x,y))
        theta += increment
    return coordinates

x= 90 # CoR
y= 94
img = sitk.GetArrayFromImage(image).reshape(size[0],size[1])
muscle_img =[0]
for i in range(3):
    mask_img = sitk.GetArrayFromImage(mask_image)[20].reshape(size[0],size[1])
    mask_img[mask_img !=(i+1)]=0
    muscle_img.append(img * mask_img)

muscle_img1 = muscle_img[3]
fi = dict()
fi2 = dict()
for col in ['distance','intensity']:
    fi2.setdefault(col, [])
for r_mm in range(18,64):
    intensities =[]
    r=round(r_mm/spacing[0])
    r = r_mm/spacing[0]
    coords = set(circle_coordinates(y,x,r))
    for coord in coords:
        intensity = muscle_img1[coord[1],coord[0]]
        if intensity:
            intensities.append(intensity)
            fi2['distance'].append(r_mm)
            fi2['intensity'].append(intensity)
        #else:
            #intensities.append(0)
    fi.setdefault(r_mm,intensities)
for key in fi:
    print(f'Radius {key}, r_pixel {round(key/spacing[0])}, length: {len(fi[key])}, FI% {round(np.mean(np.array(fi[key])),1)}')