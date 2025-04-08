#!/home/kkurkela/auto_labeler/venvs/autolabel/bin/python

# requirements
from pydicom import dcmread
import os
import argparse
import requests
import re
import json
import pdb

# suppress package warnings
requests.packages.urllib3.disable_warnings() 

# helper function
def get_files_with_extension(directory, extension):
    files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(extension):
            files.append(filename)
    return files

# parse input arguments
parser = argparse.ArgumentParser(description="Auto Labeler")
parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)
parser.add_argument("--host", default="https://xnat2.bu.edu", help="BU XNAT host", required=True)
parser.add_argument("--user", help="BU XNAT2 username", required=True)
parser.add_argument("--password", help="BU XNAT2 Password", required=True)
parser.add_argument("--project", default = "", required=True)
parser.add_argument("--subject", default = "", required=True)
parser.add_argument("--experiment", default = "", required=True)
parser.add_argument("--scan", default = "1", required=True)

args, unknown_args = parser.parse_known_args()
dicom_dir  = os.path.join(args.dicom_dir, 'DICOM')
host       = args.host
user       = args.user
password   = args.password
project    = args.project
subject    = args.subject
experiment = args.experiment
scan       = args.scan

# Set up a session
sess = requests.Session()
sess.verify = False
sess.auth = (user, password)

def is_anatomical_scan(ds):
    
    # Step 1: Exclude non-ANAT series
    series_desc = getattr(ds, "SeriesDescription", [])
    exclude_keywords = ["func", "bold", "fmap", "dti", "dwi", "localizer", "scout"]
    if any(kw in series_desc for kw in exclude_keywords):
        return False
    
    # Step 2: Check ImageType
    image_type = getattr(ds, "ImageType", [])
    if any(it in image_type for it in ["FUNCTIONAL", "DIFFUSION", "LOCALIZER"]):
        return False
    
    # Step 3: Check sequence (T1/T2/FLAIR)
    scanning_seq = getattr(ds, "ScanningSequence", "")
    if scanning_seq in ["EP"]:  # Exclude EPI (fMRI/DWI)
        return False
    
    # Step 4: Validate resolution
    slice_thickness = getattr(ds, "SliceThickness", 10.0)  # Default to 10mm if missing
    rows = getattr(ds, "Rows", 0)
    cols = getattr(ds, "Columns", 0)
    if slice_thickness > 3.0 or rows < 256 or cols < 256:
        return False
    
    # Step 5: Validate TR/TE
    tr = getattr(ds, "RepetitionTime", 0)
    te = getattr(ds, "EchoTime", 0)
    if not (400 <= tr <= 6000 and 2 <= te <= 120):  # Broad ANAT range
        return False
    
    # Step 6: Check EchoPlanarPulseSequence and (0020,0105) Number of Temporal Positions
    


    return True

## Define an is_functional_scan function

# find all files in the dicom_dir. Filter for 1.) files 2.) that end in ".dcm"
dcm_files = get_files_with_extension(dicom_dir, 'dcm')

# look at the first dicom. Read in only the header information minus the image data
path_to_first_dcm = os.path.join(dicom_dir, dcm_files[0])
first_dicom = dcmread(path_to_first_dcm, stop_before_pixels=True)
series_description = first_dicom.get('SeriesDescription')

if series_description == 'T2SPACE_1mm_256_224_p2_vNav':
    pdb.set_trace()

## Test 1 -- Is this an MR scan? If not, we cannot QA it.
if ('0008', '0060') in first_dicom:
    if first_dicom.get(('0008','0060')).value != 'MR':
        print()
        print(f"Series: {series_description}")
        print('Is NOT MR')
        quit()

## Test 2 -- Is this an brain image? If not, we cannot QA it.
if ('0018', '0015') in first_dicom:
    if first_dicom.get(('0018','0015')).value != 'BRAIN':
        print()
        print(f"Series: {series_description}")
        print('Is NOT of the Brain')
        quit()

## Test 3 -- Is this an anatomical scan?
if is_anatomical_scan(first_dicom):
    print()
    print(f"Series: {series_description}")
    print('Is ANAT')
    quit()

## Test 4 -- Is this a functional scan?
#if is_bold_scan(path_to_first_dcm):
#    print(f"Series: {series_description}")
#    print('Is BOLD')
#    quit()

# Unidenfitied scan
print()
print(f"Series: {series_description}")
print('Is unidentified')