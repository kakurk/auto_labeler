import os
import yaxil

def launch(MRsession):
    # So, at this point, everything has been labeled for this session.
    # We now need to:

    # Identify all of the tagged scans in this sessions
    auth = yaxil.auth(alias = 'xnat')
    with yaxil.session(auth) as sess:
        b = 0
        a = 0
        for scan in sess.scans(label=MRsession):
            note = scan['note']
            if 'BOLD' in note:
                print('Run BOLDQC')
                os.system(f'qsub -P drkrcs boldqc.qsub {MRsession} {b}')
                b = b+1
            if 'T1w' in note:
                print('Run ANATQC')
                os.system(f'qsub -P drkrcs anatqc.qsub {MRsession} {a}')
                a = a+1

    # For each tagged scan, launch the appropriate QA routine
