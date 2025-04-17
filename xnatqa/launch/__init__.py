import os
import yaml
import glob
import re
import xnatqa
import yaxil
import pdb

def launch(MRsession):
    # So, at this point, everything has been labeled for this session.
    # We now need to:

    # Identify all of the tagged scans in this sessions
    auth = yaxil.auth(alias = 'xnat')
    with yaxil.session(auth) as sess:
        b = 0
        for scan in sess.scans(label=MRsession):
            note = scan['note']
            if 'BOLD' in note:
                print('Run BOLDQC')
                os.system(f'qsub -P drkrcs boldqc.qsub {MRsession} {b}')
                b = b+1
            if 'T1w' in note:
                print('Run ANATQC')
            pdb.set_trace()

    # For each tagged scan, launch the appropriate QA routine
