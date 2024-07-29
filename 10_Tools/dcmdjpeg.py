import os
import subprocess
import pydicom
from multiprocessing import Process, Pool
from tqdm import tqdm


def convert_dicom(case_folder):
    output_root = r'D:\qf_output'
    for dicom in os.listdir(case_folder):
        cur_file = os.path.join(case_folder, dicom)
        try:
            ds = pydicom.dcmread(cur_file)
            pid = ds.PatientID

        except Exception as e:
            print(e)
            continue
            
        output_folder = os.path.join(output_root, pid)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.join(output_folder, dicom)
        program_to_run = [r"C:\Program Files\dcmtk-3.6.8-win64-dynamic\bin\dcmdjpeg.exe","+te",f'{cur_file}', f'{output_file}']
        result = subprocess.run(program_to_run)

if __name__=='__main__':
    
    input_root = r'D:\qf'
    output_root = r'D:\qf_output'
    case_list = os.listdir(input_root)
    '''    
    jobs = []
    
    for case in case_list:
        cur_folder = os.path.join(input_root, case)
        p = Process(target=convert_dicom,args=(cur_folder, output_root))
        p.start()
        jobs.append(p)
    for o in tqdm(jobs):
        o.join()
    '''
    args_list = []
    
    for case in case_list:
        cur_folder = os.path.join(input_root, case)
        args_list.append(cur_folder)
    with Pool(4) as p:
        p.map(convert_dicom, args_list)
