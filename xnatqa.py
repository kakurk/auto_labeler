#!/home/kkurkela/auto_labeler/venvs/autolabel/bin/python

from pydicom import dcmread
import os
import argparse
from glob import glob
from xnatqa.tag import tag_scans
from xnatqa.launch import launch

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
dicom_dir  = os.path.join(args.dicom_dir, 'SCANS')
host       = args.host
user       = args.user
password   = args.password
project    = args.project
subject    = args.subject
experiment = args.experiment
scan       = args.scan

# run xant authentication
#os.system(f'xnat_auth --alias xnat --url {host} --username {user} --password {password}')

tag_scans(dicom_dir, experiment)

launch()
