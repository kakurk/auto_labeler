import os
import yaml
from glob import glob
import re
import xnatqa

def extract_bids_suffix(bids_string):
        # Extract the BIDS suffix from a BIDS formatted string
        search_pattern = "([^_]+)$"
        match = re.search(search_pattern, bids_string)
        bids_suffix = match.group(1)
        return bids_suffix

def generate_tagger_config(dicom_dir):

    # This calls the latest version of dcm2niix WITHOUT creating the *.nii.gz files, only the BIDS metadata *.json sidecars.
    # dcm2niix automatically skips scans that it has identified as being non-BIDS (i.e., localizers, scouts)
    # dcm2niix will also include a field called "BidsGuess" containing an "educated guess" as to what the BIDS label of this scan should be.
    # This seems to work well most of the time, with the odd hicups. I include manual code here to catch the "hicups".

    # call to dcm2niix. generates a bunch of *.json text files in the current working directory.
    os.system(f"dcm2niix -s y -a y -b o -o $PWD -f 'output_%s_%d' -w 0 -m 1 -i y {dicom_dir} &>>log.txt")

    # idenfity all of these text files
    jsonFiles = glob(os.path.abspath('./output*.json'))

    # sort the found files so that they are in decensing order by series_number
    # this is probably unnecssary
    jsonFiles.sort(key=lambda f: int(re.search('(?<=output_)\d+(?=_)', f).group()))

    # initialize a dictionary to hold xnattager data
    tagger_data = dict(t1 = [], t1_move = [], t2 = [], t2_move = [], bold = [])

    # looping over the json sidecar files...
    for f in jsonFiles:

        # read in the json sidecar
        json_data = xnatqa.read_json_file(f)

        # pull out some useful meta-data that should be contained within every file
        series_description = json_data['SeriesDescription']
        series_number = json_data['SeriesNumber']
        image_type = json_data['ImageType']
        # remove the last element of the image_type list
        del image_type[-1]
        bids_guess = json_data['BidsGuess']

        # if there is a BidsGuess field...
        if 'BidsGuess' in json_data.keys():

            # if that guess was "func"
            if bids_guess[0] == 'func':

                bids_string = bids_guess[1]
                bids_suffix = extract_bids_suffix(bids_string)

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
                    exclude_keywords = ['t1', 'anat', 'mprage', 'memprage']
                    if any(kw in series_description.lower() for kw in exclude_keywords):

                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f"Bids Guess: {bids_guess}")
                        print('Relableing to T1...')
                        print()

                        tagger_data['t1'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T1w'})
                        continue

                    exclude_keywords = ['t2']
                    if any(kw in series_description.lower() for kw in exclude_keywords):

                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f'Bids Guess: {bids_guess}')
                        print('Relableing to T2...')
                        print()

                        tagger_data['t2'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T2w'})
                        continue

                    print()
                    print(f'Series Number: {series_number}')    
                    print(f'Series Description: {series_description}')
                    print(f'Bids Guess: {bids_guess}')
                    print('Labeling as BOLD...')
                    print()

                    tagger_data['bold'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#BOLD'})
                    continue

            # if the BidsGuess was "anat"...
            if bids_guess[0] == 'anat':

                bids_string = bids_guess[1]
                bids_suffix = extract_bids_suffix(bids_string)

                # if the BIDS suffix was T1w...
                if bids_suffix == 'T1w':

                    slice_thickness = json_data['SliceThickness']
                    NonlinearGradientCorrection = json_data['NonlinearGradientCorrection']

                    if slice_thickness == 8:

                        # this is a T1w VNAV setter scan.

                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f"Bids Guess: {bids_guess}")
                        print('Labeling as T1w_move...')
                        print()
                        
                        tagger_data['t1_move'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T1w_MOVE'})
                        continue

                    elif not NonlinearGradientCorrection and 'NumberOfAverages' in json_data:
                        
                        # this is a T1w scan

                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f"Bids Guess: {bids_guess}")
                        print('Labeling as T1w...')
                        print()
                        
                        tagger_data['t1'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T1w'})
                        continue

                elif bids_suffix == 'T2w':

                    if json_data['SliceThickness'] == 8:
                        
                        # this is a T2w VNAV setter scan
                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f"Bids Guess: {bids_guess}")
                        print('Labeling as T2w_move...')
                        print()

                        tagger_data['t2_move'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T2w_move'})
                        continue

                    else:

                        # this is a T2w scan
                        print()
                        print(f'Series Number: {series_number}')    
                        print(f'Series Description: {series_description}')
                        print(f"Bids Guess: {bids_guess}")
                        print('Labeling as T2w...')                        
                        print()

                        tagger_data['t2'].append({'series_description': series_description, 'image_type': image_type, 'tag': '#T2w'})
                        continue                    

    # write tagger data to a yaml file. used by the xnattagger package for uploading tags to XNAT. See github.com/harvard-nrg/xnattager
    with open('tagger.yaml', 'a') as file:
        yaml.dump(tagger_data, file)

def update_xnat_tags(MRsession):

    # make sure an xnat authentication files has already been created. See YXAIL documentation.
    assert os.path.exists(os.path.expanduser('~/.xnat_auth')), 'xnat authentication needs to be run'

    # run the command
    os.system(f'xnat_tagger.py --label {MRsession} --target-modality all --xnat-alias xnat --config tagger.yaml')

def tag_scans(dicom_dir, MRsession):
    
    # generate the xnattag config file
    generate_tagger_config(dicom_dir)
    
    # update the xnat tags
    update_xnat_tags(MRsession)

