# requirements
from pydicom import dcmread
import os
import pdb
import argparse
import requests
import re
import json
import get_files_with_extension
import update_scan_type

# parse input arguments
parser = argparse.ArgumentParser(description="Auto Labeler")
parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)
parser.add_argument("--host", default="https://xnat2.bu.edu", help="BU XNAT host", required=True)
parser.add_argument("--user", help="BU XNAT2 username", required=True)
parser.add_argument("--password", help="BU XNAT2 Password", required=True)

args, unknown_args = parser.parse_known_args()
dicom_dir = '/Users/kkurkela/Datasets/burcs/test002/test002_MR_1/2/DICOM'#args.dicom_dir
host      = args.host
user      = args.user
password  = args.password

# find all files in the dicom_dir. Filter for 1.) files 2.) that end in ".dcm"
dcm_files = get_files_with_extension(dicom_dir, 'dcm')

# look at the first dicom images. Read in only the header information minus the image data
path_to_first_dcm = os.path.join(dicom_dir, dcm_files[0])
first_dicom = dcmread(path_to_first_dcm, stop_before_pixels=True)

## pull down the qc map for determining if this scan should be marked as a BOLD, ANAT, or DWI

# Set up session
sess = requests.Session()
sess.verify = False
sess.auth = (user, password)

# Get site-level qc map
print()
print("Get site-wide Quality Control map")
r = sess.get(host + "/data/config/qc/qcmap", params={"contents": True})
if r.ok:
    qcmap = r.json()
else:
    print("Could not read site-wide QC map")

#qcmap = '{"BOLD":[{"key":"SequenceName","re":"ep*"},{"key":"PatientSex","re":"[^FM]?"}],"ANAT":[{"key":"SequenceName","re":"ep*"},{"key":"PatientSex","re":"[^FM]?"}]}'
qcmap_decoded = json.loads(qcmap)

# does this dicom meet the criteria for being labeled as a BOLD image?
passedFilter = []
for filt in qcmap_decoded['BOLD']:
    # key     = the DICOM field to check
    # pattern = regular expression to determine if this is a match or not
    key     = filt['key']
    pattern = filt['re']
    
    # extract this DICOM entry
    key_value = first_dicom.get(key)
    
    # does this DICOM entry match the regular expression?
    passed = bool(re.search(pattern, key_value))
    passedFilter.append(passed)

# label this session as BOLD or ANAT using XNAT's REST API
if all(passedFilter):
    # code for changing the "Type" field to "BOLD"
    update_scan_type(host, project, subject, experiment, scan, scantype='BOLD')

# does this dicom meet the criteria for being labeled as a BOLD image?
passedFilter = []
for filt in qcmap_decoded['ANAT']:
    # key     = the DICOM field to check
    # pattern = regular expression to determine if this is a match or not
    key     = filt['key']
    pattern = filt['re']
    
    # extract this DICOM entry
    key_value = first_dicom.get(key)
    
    # does this DICOM entry match the regular expression?
    passed = bool(re.search(pattern, key_value))
    passedFilter.append(passed)

# label this session as BOLD or ANAT using XNAT's REST API
if all(passedFilter):
    # code for changing the "Type" field to "ANAT"
    update_scan_type(host, project, subject, experiment, scan, scantype='ANAT')