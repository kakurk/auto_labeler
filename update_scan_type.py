# update scan type
import sess

project    = 'burcs'
subject    = 'test001'
experiment = 'test001_MR_2'
scan       = 2

def update_scan_type(host, project, subject, experiment, scan, scantype="BOLD"):
    print()
    print(f"Changing the Scan Type to {scantype}")
    r = sess.put(host + f"/data/projects/{project}/subjects/{subject}/experiments/{experiment}/scans/{scan}", params={"xnat:mrScanData/type":scantype})
