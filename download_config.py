# imports
import requests
import argparse
import sys
import json

# useful functions
def get(url, **kwargs):
    try:
        r = sess.get(url, **kwargs)
        r.raise_for_status()
    except (requests.ConnectionError, requests.exceptions.RequestException) as e:
        print("Request Failed")
        print("    " + str(e))
        sys.exit(1)
    return r

def cleanServer(server):
    server.strip()
    if server[-1] == '/':
        server = server[:-1]
    if server.find('http') == -1:
        server = 'https://' + server
    return server

# parse input arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("--host", default="https://cnda.wustl.edu", help="CNDA host", required=True)
parser.add_argument("--user", help="CNDA username", required=True)
parser.add_argument("--password", help="Password", required=True)
parser.add_argument("--project", help="Project", required=False)
