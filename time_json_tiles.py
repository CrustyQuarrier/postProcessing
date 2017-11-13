#!/home/bdavis/Projects/lcmap/pyccd-cmd-line/.venv/bin/python

########################################################################
#
# time_json_tiles.py
#
# bdavis
#
# 20171030
#
# Spit out all date-time stamps for "chip_update_requested" and
# "resluts_produced", which can be piped to sort to obtain start and
# end times for calculating elapsed time.
# The order in which each result appears in the .json file is not
# necessarily the order of completion.
#
# Input is .json file name.  All could be placed in a for loop call.
#
# Environment:
#
# pip freeze:
#     GDAL==2.2.1
#     numpy==1.13.1
#     PyYAML==3.12
#     requests==2.14.2
#     scikit-learn==0.19.0
#     scipy==0.19.1
#
########################################################################


########################################################################
#
# Get the necessasry modules.
#
########################################################################

import os
import sys
import time
import datetime
import multiprocessing as mp
import numpy as np
from pprint import pprint

import json


########################################################################
#
# get_json
#
# Arguments: .json file name
#
# Returns:   the .json file, as read
# 
# Verifies the file is there, and returns it.
#
########################################################################


def get_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        return None


########################################################################
#
# load_jsondata
# 
# Arguemnts: jdata, the .json file to parse
#            time_to_record, search for start or stop times
#
# Returns:   None
#
# Goes through each entry in the .json file, and spits out the start or
# stop time, depending on the time_to_record arg.
#
########################################################################

def load_jsondata(jdata, time_to_record):

    if jdata is not None:

        for j in jdata:
            if (time_to_record == "start"):
                start_time = j.get('chip_update_requested')
                print ("start_time: ", start_time)
            elif (time_to_record == "stop"):
                stop_time = j.get('result_produced')
                print ("stop_time: ", stop_time)

    return


########################################################################
# Parse arguments. time_to_record should be "start" or "stop".
########################################################################

if len(sys.argv) == 3:
    time_to_record = sys.argv[1]
    json_file_name = sys.argv[2]
else:
    print ('Invalid number of args: ', len(sys.argv))
    exit()

if time_to_record not in ('start', 'stop'):
    print ('Invalid time_to_record argument: ', time_to_record)
    print ('Usage: python time_json_tiles.py <start|stop> <json-file-name> ')
    exit()


########################################################################
# Call the function to parse the .json file.
########################################################################

load_jsondata(get_json(json_file_name), time_to_record)

