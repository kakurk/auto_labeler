#!/home/kkurkela/auto_labeler/venvs/autolabel/bin/python

from pydicom import dcmread
import os
import argparse
import re
import pdb

def sort_by_numeric_content(data):
    return sorted(data, key=lambda x: int(''.join(filter(str.isdigit, x))))

def get_files_with_extension(directory, extension):
    files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(extension):
            files.append(filename)
    return files

# parse input arguments
parser = argparse.ArgumentParser(description="field printer")
parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)

# /data/xnat/archive/ZukScala/arc001/250604_LA019/SCANS
args, unknown_args = parser.parse_known_args()
dicom_dir  = args.dicom_dir

# identify the fields in dicom_dir

files = os.listdir(dicom_dir)
files_sorted = sort_by_numeric_content(files)

# /data/xnat/archive/ZukScala/arc001/250604_LA019/SCANS
for d in files_sorted:
    dpath = os.path.join(dicom_dir, d, 'DICOM')
    dcm_files = get_files_with_extension(dpath, 'dcm')
    path_to_first_dcm = os.path.join(dpath, dcm_files[0])
    first_dicom = dcmread(path_to_first_dcm, stop_before_pixels=True)
    seires_description = first_dicom.get('SeriesDescription')
    psn = first_dicom.get(('0020','0105')).value
    series_number = first_dicom.get('SeriesNumber')

    print('')
    print(f'Scan Number: {series_number}')
    print(f'Series Description: {seires_description}')
    print(f'Pulse Sequence Name {psn}')
    print('')

