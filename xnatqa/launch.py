import os
import yaxil
import argparse
import re

def main():
    # So, at this point, everything has been labeled for this session.
    # We now need to:

    # Identify all of the tagged scans in this sessions
    # For each tagged scan, launch the appropriate QA routine

    # parse input arguments
    parser = argparse.ArgumentParser(description="XNAT QA Workflow")
    parser.add_argument("--experiment", default = "", required=True)
    parser.add_argument("--dryrun", default = "", action='store_true', help="Run in dry run mode: No launching of jobs")

    args, unknown_args = parser.parse_known_args()
    MRsession = args.experiment
    dryrun    = args.dryrun

    # make sure an xnat authentication files has already been created. See YXAIL documentation.
    assert os.path.exists(os.path.expanduser('~/.xnat_auth')), 'xnat authentication needs to be run'

    # authenticate with xnat using the ~/.xnat_auth file
    auth = yaxil.auth(alias = 'xnat')

    # open and automatically close a connection to XNAT using the auth
    with yaxil.session(auth) as sess:
        # keep track of the number of BOLD (b) and ANAT (a) scans idenfified

        # for each scan in this session...
        for scan in sess.scans(label=MRsession):

            # this scan's note
            note = scan['note']
            id = scan['ID']
            type = scan['type']
            SeriesDesc = scan['series_description']
            quality = scan['quality']

            # if that note has a "#BOLD" tag...
            if '#BOLD' in note:

                run = re.search('[0-9]{3}', note)
                run = int(run.group())

                print('')
                print('Run BOLDQC:')
                print(f'{id}\t{type}\t{SeriesDesc}\t{quality}\t{note}')
                print(f'qsub -P drkrcs boldqc.qsub {MRsession} {run}')
                print('')
                if not dryrun:
                    os.system(f'qsub -P drkrcs boldqc.qsub {MRsession} {run}')

            # if that note has a "#T1w" tag...
            if '#T1w' in note:

                run = re.search('[0-9]{3}', note)
                run = int(run.group())

                print('')
                print('Run ANATQC:')
                print(f'{id}\t{type}\t{SeriesDesc}\t{quality}\t{note}')             
                print(f'qsub -P drkrcs anatqc.qsub {MRsession} {run}')
                print('')
                if not dryrun:
                    os.system(f'qsub -P drkrcs anatqc.qsub {MRsession} {run}')