#/bin/bash
# A wrapper over autolabel

readarray -t dirs_to_search < directories_to_search.txt

XNAT_HOST='https://xnat2.bu.edu'
XNAT_USER='kkurkela'
XNAT_PASS='Q8ZTq!rC!w!4xkFBU24'
project='ZukScala'
subject='250604'
experiment='250604_LA019'

for dir in "${dirs_to_search[@]}"
do
    ./auto_label.py --user $XNAT_USER --host $XNAT_HOST --password $XNAT_PASS --dicom_dir $dir --project $project --subject $subject --experiment $experiment --scan 1
done