import os
import argparse
from xnatqa.tag import tag_scans

def main():

    # parse input arguments
    parser = argparse.ArgumentParser(description="XNAT QA Workflow")
    parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)
    parser.add_argument("--experiment", default = "", required=True)

    args, unknown_args = parser.parse_known_args()
    dicom_dir  = os.path.join(args.dicom_dir, 'SCANS')
    experiment = args.experiment

    # run xnat authentication for this container. writes an ~/.xnat_auth file to the home directory
    # this file is used in all subsequent calls to XNAT
    os.system(f'xnat_auth --alias xnat --url $XNAT_HOST --username $XNAT_USER --password $XNAT_PASS')

    # tag all scans in this session
    tag_scans(dicom_dir, experiment)

if __name__ == "__main__":
    main()