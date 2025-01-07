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
dicom_dir  = args.dicom_dir
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

# load the XNAT REST API Site-wide Config
r = sess.get(host + "/data/config/autolabel/autolabelmap", params={"contents": True})
if r.ok:
    qcmap_decoded = r.json()
else:
    print("Could not read site-wide BIDS map")

# find all files in the dicom_dir. Filter for 1.) files 2.) that end in ".dcm"
dcm_files = get_files_with_extension(dicom_dir, 'dcm')

# look at the first dicom. Read in only the header information minus the image data
path_to_first_dcm = os.path.join(dicom_dir, dcm_files[0])
first_dicom = dcmread(path_to_first_dcm, stop_before_pixels=True)

filterRequirments = {}

for scantype in qcmap_decoded:
    
    print()
    print(scantype)
    print()

    # does this dicom meet the criteria for being labeled as a SCANTYPE image?
    passedFilter = []
    for filt in qcmap_decoded[scantype]:
        # key     = the DICOM field to check
        # pattern = regular expression to determine if this is a match or not
        key     = filt['key']
        pattern = filt['re']
        
        print(f"DICOM Field: {key}")
        print(f"Matching pattern: {pattern}")

        # extract this DICOM entry
        key_value = first_dicom.get(key)
        
        # does this DICOM entry match the regular expression?
        passed = bool(re.search(pattern, key_value))
        passedFilter.append(passed)
    
    # does this scan meet ALL of the filter requirements?
    filterRequirments[scantype] = all(passedFilter)

print()
print(filterRequirments)
print()

numOfLabelsDiscovered = sum(filterRequirments.values())
assert numOfLabelsDiscovered <= 1, 'More than 1 Label Discovered'

# label this session as BOLD or ANAT or DWI using XNAT's REST API
for scantype in filterRequirments:

    # if this scan met all of the requirements for this scantype...
    if filterRequirments[scantype]:

        # code for changing the "Type" field to "SCANTYPE"
        print()
        print(f"Changing the Scan Type to {scantype}")
        r = sess.put(host + f"/data/projects/{project}/subjects/{subject}/experiments/{experiment}/scans/{scan}", params={"xnat:mrScanData/type":scantype})
        print(r.ok)
        print()

# close the 
sess.close()