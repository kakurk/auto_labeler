import os
import yaxil

def launch(MRsession):
    # So, at this point, everything has been labeled for this session.
    # We now need to:

    # Identify all of the tagged scans in this sessions
    # For each tagged scan, launch the appropriate QA routine

    # authenticate with xnat using the ~/.xnat_auth file created earlier in the workflow
    auth = yaxil.auth(alias = 'xnat')

    # open and automatically close a connection to XNAT using the auth
    with yaxil.session(auth) as sess:
        # keep track of the number of BOLD (b) and ANAT (a) scans idenfified
        b = 0
        a = 0

        # for each scan in this session...
        for scan in sess.scans(label=MRsession):

            # this scan's note
            note = scan['note']

            # if that note has a "#BOLD" tag...
            if '#BOLD' in note:
                print('Run BOLDQC')
                os.system(f'qsub -P drkrcs boldqc.qsub {MRsession} {b}')
                b+=1

            # if that note has a "#T1w" tag...
            if '#T1w' in note:
                print('Run ANATQC')
                os.system(f'qsub -P drkrcs anatqc.qsub {MRsession} {a}')
                a+=1