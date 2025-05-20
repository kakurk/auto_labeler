#!/bin/bash

# XNAT Session Monitor Script
# Checks for newly created scan sessions on an XNAT instance

# Configuration
#  Before running this script, the user MUST create the following enviromental variables:
#  export XNAT_USER=username
#  export XNAT_PASS=password

# force shell to exit immediately if any of the commands exits with a non-zero status 
set -e

QAHOME=/home/xnat/qa
OGHOME=$HOME
export HOME=$QAHOME
XNAT_HOST="https://xnat2.bu.edu"
PROJECT_ID=""  # Leave empty to check all accessible projects
CHECK_INTERVAL=3600  # Time between checks in seconds (default: 1 hour)
STATE_FILE="$HOME/.xnat_last_checked"  # File to store last check timestamp

# source the python virtual enviorment
VENV_PATH="$HOME/venvs/xnatqa"
source "$VENV_PATH/bin/activate"

# add dcm2niix to the PATH if it is not already there
if ! command -v dcm2niix &> /dev/null; then
    echo "dcm2niix is not on the PATH" &>2
    exit 1
fi

# make sure dcm2niix is the proper version:
DCM2NIIX_VERSION=$(dcm2niix -v | tail -n 1)
if [ ! $DCM2NIIX_VERSION = "v1.0.20241211" ]; then
    echo "Incorrect dcm2niix version detected. This routine requires version v1.0.20241211" &>2
    echo "Detected version: $DCM2NIIX_VERSION" &>2
    exit 1
fi

# Function to authenticate with XNAT and get JSESSIONID
authenticate() {
    SESSION_ID=$(curl -s -k -u "$XNAT_USER:$XNAT_PASS" -X POST "$XNAT_HOST/data/JSESSION" | tr -d '"')
    echo "$SESSION_ID"
}

# The current timestamp
current_timestamp=$(date)

# Function to get today's date in a format the is Kosher with XNAT's API
todays_date() {
    date -u +"%m/%d/%Y"
}

# Function to get tomorrow's date in a format the is Kosher with XNAT's API
tomorrows_date() {
   date -d "tomorrow" +%m/%d/%Y
}

# Function to check if response is HTML
is_html_response() {
    local content="$1"
    [[ "$content" == *"<html"* ]] || [[ "$content" == *"<!DOCTYPE"* ]] || [[ "$content" == *"<head"* ]]
}

# function that returns all sessions inserted today
get_todays_sessions() {

    local jsession="$1"
    local today=$(todays_date)
    local tomorrow=$(tomorrows_date)

    # Build the API URL, appending the project id and todays date as necessary
    local api_url="$XNAT_HOST/data/experiments"
    if [ -n "$PROJECT_ID" ]; then
        api_url="$api_url?project=$PROJECT_ID"
        api_url="$api_url&columns=project,insert_date,label&insert_date=$today-$tomorrow"
    else
        api_url="$api_url?columns=project,insert_date,label&insert_date=$today-$tomorrow"
    fi

    # Get the sessions
    RAW_RESPONSE=$(curl -s -k -b "JSESSIONID=$jsession" -H "Accept: application/json" "$api_url")

    # Check if response is HTML. This indicates some sort of error has occured. If its not html, return the raw json response
    if is_html_response "$RAW_RESPONSE"; then
        echo "" >&2
        echo "ERROR: Received HTML response instead of JSON data" >&2
        echo "Possible authentication failure" >&2
        echo "" >&2
        echo "Response from XNAT:" >&2
        echo "" >&2
        echo "$RAW_RESPONSE" >&2
        echo "" >&2
        return 1
    else
        echo $RAW_RESPONSE
    fi
}

# Main script
echo ""
echo "XNAT Session Monitor - Started at $current_timestamp"
echo ""

# Get or create last checked timestamp
if [ -f "$STATE_FILE" ]; then
    LAST_CHECKED=$(cat "$STATE_FILE")
else
    LAST_CHECKED=""
fi

echo "Last checked: ${LAST_CHECKED:-"Never"}"

# Authenticate to XNAT
JSESSION=$(authenticate)
if [ -z "$JSESSION" ]; then
    echo "ERROR: Authentication failed"
    exit 1
fi

# Get todays sessions
echo ""
echo "Retrieving today's sessions..."
TODAYS_SESSIONS=$(get_todays_sessions "$JSESSION")

# extract relevant data as bash arrays
mapfile -t ID < <(jq -r '.ResultSet.Result[].ID' <<< $TODAYS_SESSIONS)
mapfile -t label < <(jq -r '.ResultSet.Result[].label' <<< $TODAYS_SESSIONS)
mapfile -t insert_date < <(jq -r '.ResultSet.Result[].insert_date' <<< $TODAYS_SESSIONS)
mapfile -t projects < <(jq -r '.ResultSet.Result[].project' <<< $TODAYS_SESSIONS)

# Have any of these sessions been inserted in the intervening time period?
start_datetime=$LAST_CHECKED
end_datetime=$current_timestamp

# Convert start and end to seconds since epoch for comparison
start_sec=$(date -d "$start_datetime" +%s)
end_sec=$(date -d "$end_datetime" +%s)

echo ""
echo "Checking if sessions were inserted between $start_datetime and $end_datetime"
echo "--------------------------------------------------"

# Loop through the array and check each datetime
c=0
for dt in "${insert_date[@]}"; do

    # Convert current datetime to seconds since epoch
    dt_sec=$(date -d "$dt" +%s)

    # Determine if this insert time is between START and END. Exclude the QA project.
    if (( dt_sec >= start_sec && dt_sec <= end_sec )) && [[ "$project" != "qa" ]]; then

        echo ""
        echo "Session: ${label[$c]} inserted at $dt is WITHIN the range"
        echo ""

        # code for labeling and launching

        # In order to label, I need the full path to where the scans are store on this machine
        # XNAT archives data in the following directory structure:
        # structure: /data/xnat/archive/%PROJECT%/arc001/%SESSION%/SCANS/
        # where %PROJECT% and %SESSION% are the project and session labels respectively
        # for example: /data/xnat/archive/burcs/arc001/test001_MR_1/SCANS/
        path_to_scans=/data/xnat/archive/${projects[$c]}/arc001/${label[$c]}/SCANS/

        # make sure "path_to_scans" exists. Throw an error if it does not.
        if [ ! -d $path_to_scans ]; then
            echo "Scans directory does not exist for project: ${projects[$c]} session: ${label[$c]}" >&2
            echo $path_to_scans >&2
            exit 1
        fi

        # check yaxil authentication
        if [ ! -f ~/.xnat_auth ]; then
            echo "Need to run yaxil XNAT authentication for this user" >&2
            exit 1
        fi

        # run the labeling process
        echo ""
        echo "Tagging scans for Session ${label[$c]}..."
        echo ""
        tagger --dicom_dir $path_to_scans --experiment ${label[$c]} --working_dir /tmp --dryrun

        # launch jobs on the SCC for the QA reports.
        # launches 1 job for each tagged scan in this session.
        # BOLDQC jobs take < 1hr
        # ANATQC jobs take ~3-4 hrs
        launch --experiment ${label[$c]} --dryrun

    else
        echo ""
        echo "Session ${label[$c]} inserted at $dt is OUTSIDE the range"
        echo ""
    fi

    # advance the counter
    c=$((c + 1))

done

# Update last checked timestamp
NEW_TIMESTAMP=$(date)
echo "$NEW_TIMESTAMP" > "$STATE_FILE"
echo "Updated last checked timestamp to: $NEW_TIMESTAMP"
echo ""

# Logout
curl -s -k -b "JSESSIONID=$JSESSION" "$XNAT_HOST/data/JSESSION" -X DELETE > /dev/null

# confirm check complete
echo "Check complete. Next check in $CHECK_INTERVAL seconds."

# deactivate the python virtual enviroment
deactivate

# reset HOME
export HOME=OGHOME