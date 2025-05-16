import os
import argparse
from xnatqa.tag import generate_tagger_config
from xnatqa.tag import generate_tagger_yaml
from xnatqa.tag import update_xnat_tags
import shutil

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
     # create a working directory to write temporary files
    this_session_working_dir = os.path.join(working_dir, 'xnattager', experiment)
    if os.path.isdir(this_session_working_dir):
        shutil.rmtree(this_session_working_dir)
    os.makedirs(this_session_working_dir)

    # generate the xnattag config file
    generate_tagger_config(dicom_dir, this_session_working_dir)
    
    # general the yaml
    generate_tagger_yaml(this_session_working_dir)

    # update the xnat tags
    if not dryrun:
        update_xnat_tags(experiment, this_session_working_dir)

if __name__ == "__main__":
    main()