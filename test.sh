#!/bin/bash

XNAT_USER=kkurkela
XNAT_HOST=https:://xnat2.bu.edu
XNAT_PASS=$(<pass.txt)
DICOMDIR=/Users/kkurkela/Datasets/burcs/test002/test002_MR_1/3/DICOM
PROJ_ID=burcs
SUBJ_ID=test002
SESS_ID=test002_MR_1
SCAN_ID=3
QCMAPJSON=./qmap.json

python auto_label.py --user $XNAT_USER --host $XNAT_HOST --password $XNAT_PASS --dicom_dir $DICOMDIR --project $PROJ_ID --subject $SUBJ_ID --experiment $SESS_ID --scan $SCAN_ID --qcmapjson $QCMAPJSON