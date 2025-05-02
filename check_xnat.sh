#!/bin/bash

# XNAT Session Monitor Script
# Checks for newly created scan sessions on an XNAT instance

# Configuration
XNAT_HOST="https://xnat2.bu.edu"
XNAT_USER="kkurkela"
XNAT_PASS="Q8ZTq!rC!w!4xkFBU24"
PROJECT_ID=""  # Leave empty to check all accessible projects
CHECK_INTERVAL=3600  # Time between checks in seconds (default: 1 hour)
STATE_FILE="$HOME/.xnat_last_checked"  # File to store last check timestamp

# Function to authenticate and get JSESSIONID
authenticate() {
    SESSION_ID=$(curl -s -k -u "$XNAT_USER:$XNAT_PASS" -X POST "$XNAT_HOST/data/JSESSION" | tr -d '"')
    echo "$SESSION_ID"
}

# Function to get todays date in a format the is Kosher with XNAT's API
current_timestamp=$(date)

todays_date() {
    date -u +"%m/%d/%Y"
}

# Function to check if response is HTML
is_html_response() {
    local content="$1"
    [[ "$content" == *"<html"* ]] || [[ "$content" == *"<!DOCTYPE"* ]] || [[ "$content" == *"<head"* ]]
}

get_todays_sessions() {

    local jsession="$1"
    local today=$(todays_date)
    
    # Build the API URL
    local api_url="$XNAT_HOST/data/experiments"
    if [ -n "$PROJECT_ID" ]; then
        api_url="$api_url?project=$PROJECT_ID"
        api_url="$api_url&date=$today"
    else
        api_url="$api_url?date=$today"
    fi
    
    # Get the sessions
    RAW_RESPONSE=$(curl -s -k -b "JSESSIONID=$jsession" -H "Accept: application/json" "$api_url")
 
    # Check if response is HTML
    if is_html_response $RAW_RESPONSE; then
        echo "ERROR: Received HTML response instead of JSON data" >&2
        echo "Possible authentication failure or invalid endpoint" >&2
        echo "Response starts with:" >&2
        echo $RAW_RESPONSE
        return 1
    else
        echo $RAW_RESPONSE
    fi
}

# Main script
echo "XNAT Session Monitor - Started at $(current_timestamp)"

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
echo "Checking for todays sessions..."
TODAYS_SESSIONS=$(get_todays_sessions "$JSESSION")

# extract relevant data as bash arrays
mapfile -t ID < <(jq -r '.ResultSet.Result[].ID' <<< $TODAYS_SESSIONS)
mapfile -t label < <(jq -r '.ResultSet.Result[].label' <<< $TODAYS_SESSIONS)
mapfile -t insert_date < <(jq -r '.ResultSet.Result[].insert_date' <<< $TODAYS_SESSIONS)

# Have any of these sessions been inserted in the intervening time period?
echo $LAST_CHECKED
start_datetime=$LAST_CHECKED
end_datetime=$current_timestamp

# Convert start and end to seconds since epoch for comparison
start_sec=$(date -d "$start_datetime" +%s)
end_sec=$(date -d "$end_datetime" +%s)
echo $start_sec


echo "Checking which datetimes fall between $start_datetime and $end_datetime"
echo "--------------------------------------------------"

# Loop through the array and check each datetime
for dt in "${insert_date[@]}"; do

    # Convert current datetime to seconds since epoch
    dt_sec=$(date -d "$dt" +%s)
    
    # Perform the comparison
    if (( dt_sec >= start_sec && dt_sec <= end_sec )); then
        echo "$dt is WITHIN the range"
    else
        echo "$dt is OUTSIDE the range"
    fi
done

# if [ -n "$NEW_SESSIONS" ]; then
#     echo "New sessions found:"
#     echo "$NEW_SESSIONS" | while read -r line; do
#         echo "  - $line"
#     done
# else
#     echo "No new sessions found."
# fi

# Update last checked timestamp
NEW_TIMESTAMP=$(todays_date)
echo "$NEW_TIMESTAMP" > "$STATE_FILE"
echo "Updated last checked timestamp to: $NEW_TIMESTAMP"

# Logout
curl -s -k -b "JSESSIONID=$JSESSION" "$XNAT_HOST/data/JSESSION" -X DELETE > /dev/null

echo "Check complete. Next check in $CHECK_INTERVAL seconds."