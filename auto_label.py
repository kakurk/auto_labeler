#!/home/kkurkela/auto_labeler/venvs/autolabel/bin/python

# requirements
from pydicom import dcmread
import os
import argparse
import requests
import re
import json
import pdb
from glob import glob
import yaml

# suppress package warnings
requests.packages.urllib3.disable_warnings()

# helper function
def get_files_with_extension(directory, extension):
    files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(extension):
            files.append(filename)
    return files

# parse input arguments
parser = argparse.ArgumentParser(description="Auto Labeler")
parser.add_argument("--dicom_dir", default="/input", help = "where the DICOMs are located", required=True)
parser.add_argument("--host", default="https://xnat2.bu.edu", help="BU XNAT host", required=True)
parser.add_argument("--user", help="BU XNAT2 username", required=True)
parser.add_argument("--password", help="BU XNAT2 Password", required=True)
parser.add_argument("--project", default = "", required=True)
parser.add_argument("--subject", default = "", required=True)
parser.add_argument("--experiment", default = "", required=True)
parser.add_argument("--scan", default = "1", required=True)

args, unknown_args = parser.parse_known_args()
dicom_dir  = os.path.join(args.dicom_dir, 'SCANS')
host       = args.host
user       = args.user
password   = args.password
project    = args.project
subject    = args.subject
experiment = args.experiment
scan       = args.scan

# run xant authentication
#os.system(f'xnat_auth --alias xnat --url {host} --username {user} --password {password}')

def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The JSON data as a Python dictionary, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {file_path}")
        return None

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_presenter)

def update_tagger_yaml(modality, series_description, image_type, tag):
    # tag scan using xnattagger

    # write a xnattagger configuration file for this scan
    data = {modality: [{'series_description': series_description, 'image_type': image_type, 'tag': tag}]}
    with open('tagger.yaml', 'a') as file:
        yaml.dump(data, file)
    
def tag_scans(MRsession, modality):

    # make sure an xnat authentication files has already been created. See YXAIL documentation.
    assert os.path.exists('~/.xnat_auth'), 'xnat authentication needs to be run'

    # run the command
    os.system(f'xnat_tagger.py --label {MRsession} target-modality {modality} --xnat-alias xnat --config tagger.yaml')

# This calls the latest version of dcm2niix WITHOUT creating the *.nii.gz files, only the BIDS metadata *.json sidecars.
# dcm2niix automatically skips scans that it has identified as being non-BIDS (i.e., localizers, scouts)
# dcm2niix will also include a field called "BidsGuess" containing an "educated guess" as to what the BIDS label of this scan should be.
# This seems to work well most of the time, with the odd hicups. I include manual code here to catch the "hicups".

# call to dcm2niix. generates a bunch of *.json text files in the current working directory.
os.system(f"dcm2niix -s y -a y -b o -o $PWD -f 'output_%s_%d' -w 0 -m 1 -i y {dicom_dir} &>>log.txt")

# idenfity all of these text files
jsonFiles = glob('output*.json')

# sort the found files so that they are in decensing order by series_number
jsonFiles.sort(key=lambda f: int(re.search('(?<=output_)\d+(?=_)', f).group()))

# initalize some counters to be used within the for loop below.
t1_move = 0
t1      = 0
t2_move = 0
t2      = 0
bold    = 0

# looping over the json sidecar files...
for f in jsonFiles:

    # read in the json sidecar
    json_data = read_json_file(f)

    # pull out some useful meta-data that should be contained within every file
    series_description = json_data['SeriesDescription']
    series_number = json_data['SeriesNumber']
    image_type = json_data[]

    # if there is a BidsGuess field...
    if 'BidsGuess' in json_data.keys():

        # if that guess was "func"
        if json_data['BidsGuess'][0] == 'func':

            # extract the specific bids suffix. This is at the end of the file name following an underscore (e.g., sub-01_ses-01_task-rest_bold)
            search_pattern = "([^_]+)$"
            match = re.search(search_pattern, json_data['BidsGuess'][1])
            bids_suffix = match.group(1)

            # if the suffix is "bold"...
            if bids_suffix == 'bold':

                # there are a couple of common problems with the BidsGuess feature. One is that it does NOT properly identify "SBREF" scans. Make sure this is not an "SBREF" scan. Here I search for the keyword "SBREF" to be somewhere within the study description name.
                sbref_keywords = ['sbref']

                if any(kw in series_description.lower() for kw in sbref_keywords):

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print('Is an SBREF scan. Ignoring...')
                    print()
                    continue

                # double check that it is, in fact, a BOLD image
                # this will be a rudimentary check, attempting to catch glaring errors by looking for the presence of keywords in the series description
                exclude_keywords = ['t1', 't2', 'anat', 'mprage', 'memprage', 'dwi', 'dMRI']
                if any(kw in series_description.lower() for kw in exclude_keywords):

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()
                    print('Likely Mislabeled...')

                else:

                    bold = bold + 1

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()

                    print('Changing label to BOLD...')
                    print('============================================================')
                    print('Scan     Type     Series Desc     Usability    Files    Note')
                    print('         BOLD                                               ')
                    print('============================================================')

                    # update the xnat_tagger.yaml
                    update_tagger_yaml(series_description, image_type, f'#BOLD_00{bold}', experiment, 'bold')

        # if the BidsGuess was "anat"...
        if json_data['BidsGuess'][0] == 'anat':

            # The BIDS suffix
            search_pattern = "([^_]+)$"
            match = re.search(search_pattern, json_data['BidsGuess'][1])
            bids_suffix = match.group(1)

            # if the BIDS suffix was T1w...
            if bids_suffix == 'T1w':

                slice_thickness = json_data['SliceThickness']
                NonlinearGradientCorrection = json_data['NonlinearGradientCorrection']

                if slice_thickness == 8:
                    # this is a VNAV setter scan.
                    t1_move = t1_move + 1

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()

                    print(f'Labeling ANAT #T1w_MOVE_00{t1_move}')
                    print('============================================================')
                    print('Scan     Type     Series Desc     Usability    Files    Note')
                    print(f'                                                        #T1w_MOVE_00{t1_move}')
                    print('============================================================')

                elif not NonlinearGradientCorrection and 'NumberOfAverages' in json_data:
                    # this is a T1w scan
                    t1 = t1 + 1

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()

                    print(f'Labeling ANAT #T1w_00{t1}')
                    print('============================================================')
                    print('Scan     Type     Series Desc     Usability    Files    Note')
                    print(f'                                                        #T1w_00{t1}')
                    print('============================================================')

            elif bids_suffix == 'T2w':

                if json_data['SliceThickness'] == 8:
                    # this is a VNAV setter scan.
                    t2_move = t2_move + 1

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()

                    print(f'Labeling ANAT #T2w_MOVE_00{t2_move}')
                    print('============================================================')
                    print('Scan     Type     Series Desc     Usability    Files    Note')
                    print(f'                                                       #T2w_MOVE_00{t2_move}')
                    print('============================================================')                 
                else:
                    # this is a T2w scan
                    t2 = t2 + 1

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f"Bids Guess: {json_data['BidsGuess']}")
                    print()

                    print(f'Labeling ANAT #T2w_00{t2}')
                    print('============================================================')
                    print('Scan     Type     Series Desc     Usability    Files    Note')
                    print(f'                                                        #T2w_00{t2}')
                    print('============================================================')               
