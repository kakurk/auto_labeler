import os
import argparse
from xnatqa.tag import tag_scans

def main():

    # parse input arguments
    parser = argparse.ArgumentParser(description="XNAT QA Workflow")
    parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)
    parser.add_argument("--experiment", default = "", required=True)
    parser.add_argument("--working_dir", default = '/tmp', help="Where should intermediate files get written?")
    parser.add_argument("--dryrun", default = "", action='store_true', help="Run in dry run mode: No upload to XNAT")

    args, unknown_args = parser.parse_known_args()
    dicom_dir   = os.path.join(args.dicom_dir)
    experiment  = args.experiment
    working_dir = args.working_dir    
    dryrun      = args.dryrun

    # tag all scans in this session
    tag_scans(dicom_dir, experiment, working_dir, dryrun)

if __name__ == "__main__":
    main()